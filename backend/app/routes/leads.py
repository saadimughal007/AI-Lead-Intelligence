
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate
from app.services.lead_scoring import score_lead
from app.services.lead_enrichment import enrich_company


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leads", tags=["Leads"])


# CREATE LEAD
@router.post(
    "/",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lead(
    payload: LeadCreate,
    db: Session = Depends(get_db),
):
    lead = Lead(**payload.model_dump())

    db.add(lead)

    try:
        db.commit()
        db.refresh(lead)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A lead with this email already exists.",
        )

    return lead


# GET ALL LEADS
@router.get("/", response_model=list[LeadResponse])
def get_leads(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    lead_status: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    statement = select(Lead).offset(skip).limit(limit)

    if lead_status:
        statement = statement.where(Lead.status == lead_status)

    return db.scalars(statement).all()


# GET SINGLE LEAD
@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    return lead


# UPDATE LEAD
@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(lead, field, value)

    try:
        db.commit()
        db.refresh(lead)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This email is already assigned to another lead.",
        )

    return lead


# DELETE LEAD
@router.delete(
    "/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    db.delete(lead)
    db.commit()

    return None


# AI LEAD SCORING
@router.post(
    "/{lead_id}/score",
    response_model=LeadResponse,
)
def score_existing_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    lead_data = {
        "full_name": lead.full_name,
        "email": lead.email,
        "company": lead.company,
        "website": lead.website,
        "job_title": lead.job_title,
        "industry": lead.industry,
        "country": lead.country,
        "lead_source": lead.lead_source,
        "status": lead.status,
        "notes": lead.notes,
        "company_description": lead.company_description,
        "company_services": lead.company_services,
        "target_audience": lead.target_audience,
        "business_model": lead.business_model,
    }

    try:
        result = score_lead(lead_data)

        lead.ai_score = result["score"]
        lead.ai_category = result["category"]
        lead.icp_match = result["icp_match"]
        lead.ai_reasoning = result["reasoning"]
        lead.recommended_action = result["recommended_action"]
        lead.ai_confidence = result["ai_confidence"]
        lead.missing_information = result["missing_information"]
        lead.score_breakdown = result["score_breakdown"]

        db.commit()
        db.refresh(lead)

    except Exception as error:
        db.rollback()
        logger.exception(
            "AI lead scoring failed for lead_id=%s",
            lead_id,
        )

        raise HTTPException(
            status_code=502,
            detail="AI lead scoring failed. Check the Gemini service and response validation.",
        ) from error

    return lead


# AI COMPANY ENRICHMENT
@router.post(
    "/{lead_id}/enrich",
    response_model=LeadResponse,
)
def enrich_existing_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    if not lead.website:
        raise HTTPException(
            status_code=400,
            detail="This lead does not have a website URL.",
        )

    try:
        result = enrich_company(lead.website)

    except ValueError as error:
        lead.enrichment_status = "failed"
        lead.enrichment_notes = str(error)

        db.commit()

        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except Exception as error:
        db.rollback()
        logger.exception(
            "Company enrichment failed for lead_id=%s",
            lead_id,
        )

        raise HTTPException(
            status_code=502,
            detail="Company enrichment failed. Check the website and Gemini service.",
        ) from error

    lead.company_description = result["company_description"]
    lead.company_services = result["company_services"]
    lead.target_audience = result["target_audience"]
    lead.business_model = result["business_model"]

    lead.enrichment_status = result["enrichment_status"]
    lead.enrichment_source_url = result["enrichment_source_url"]
    lead.enrichment_confidence = result["enrichment_confidence"]
    lead.enrichment_notes = result["enrichment_notes"]
    lead.enrichment_evidence = result["enrichment_evidence"]

    lead.enriched_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(lead)

    return lead
