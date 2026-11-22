
import logging
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.lead import Lead
from app.models.outreach import Outreach
from app.schemas.outreach import (
    OutreachGenerateRequest,
    OutreachResponse,
    OutreachUpdate,
)
from app.services.outreach_generator import generate_outreach_drafts


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/outreach", tags=["AI Outreach"])


def get_outreach_or_404(outreach_id: int, db: Session) -> Outreach:
    record = db.get(Outreach, outreach_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outreach record not found.",
        )

    return record


def commit_changes(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        logger.exception("Database commit failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed.",
        ) from error


@router.post(
    "/{lead_id}/generate",
    response_model=list[OutreachResponse],
    status_code=status.HTTP_201_CREATED,
)
def generate_for_lead(
    lead_id: int,
    payload: OutreachGenerateRequest,
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)

    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found.",
        )

    lead_data = {
        "full_name": lead.full_name,
        "email": lead.email,
        "company": lead.company,
        "website": lead.website,
        "job_title": lead.job_title,
        "industry": lead.industry,
        "country": lead.country,
        "company_description": lead.company_description,
        "company_services": lead.company_services,
        "target_audience": lead.target_audience,
        "business_model": lead.business_model,
        "ai_score": lead.ai_score,
        "ai_category": lead.ai_category,
        "ai_reasoning": lead.ai_reasoning,
        "recommended_action": lead.recommended_action,
    }

    try:
        drafts = generate_outreach_drafts(
            lead_data,
            payload.model_dump(exclude_none=True),
        )

    except Exception as error:
        logger.exception(
            "AI outreach generation failed for lead_id=%s",
            lead_id,
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI generation failed: {type(error).__name__}",
        ) from error

    if len(drafts) != 4:
        logger.error(
            "Expected 4 outreach drafts, received %s",
            len(drafts),
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI provider returned an unexpected number of drafts.",
        )

    records = []

    for draft in drafts:
        records.append(
            Outreach(
                lead_id=lead.id,
                channel=draft["channel"],
                message_type=draft["message_type"],
                tone=payload.tone,
                subject=draft.get("subject"),
                message=draft["message"],
                call_to_action=draft.get("call_to_action"),
                status="draft",
            )
        )

    db.add_all(records)
    commit_changes(db)

    try:
        for record in records:
            db.refresh(record)

    except SQLAlchemyError as error:
        db.rollback()
        logger.exception("Failed to refresh generated outreach records")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve the generated outreach records.",
        ) from error

    return records


@router.get("/", response_model=list[OutreachResponse])
def list_outreach(
    lead_id: int | None = Query(default=None, ge=1),
    outreach_status: Literal[
        "draft", "approved", "rejected", "sent"
    ] | None = Query(default=None, alias="status"),
    channel: Literal["email", "linkedin"] | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    statement = select(Outreach).order_by(Outreach.generated_at.desc())

    if lead_id is not None:
        statement = statement.where(Outreach.lead_id == lead_id)

    if outreach_status is not None:
        statement = statement.where(Outreach.status == outreach_status)

    if channel is not None:
        statement = statement.where(Outreach.channel == channel)

    statement = statement.offset(offset).limit(limit)

    return db.scalars(statement).all()


@router.get("/{outreach_id}", response_model=OutreachResponse)
def get_outreach(
    outreach_id: int,
    db: Session = Depends(get_db),
):
    return get_outreach_or_404(outreach_id, db)


@router.put("/{outreach_id}", response_model=OutreachResponse)
def update_outreach(
    outreach_id: int,
    payload: OutreachUpdate,
    db: Session = Depends(get_db),
):
    record = get_outreach_or_404(outreach_id, db)

    if record.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft outreach records can be edited.",
        )

    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(record, field, value)

    commit_changes(db)
    db.refresh(record)

    return record


@router.post("/{outreach_id}/approve", response_model=OutreachResponse)
def approve_outreach(
    outreach_id: int,
    db: Session = Depends(get_db),
):
    record = get_outreach_or_404(outreach_id, db)

    if record.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft outreach records can be approved.",
        )

    record.status = "approved"
    record.approved_at = datetime.now(timezone.utc)

    commit_changes(db)
    db.refresh(record)

    return record


@router.post("/{outreach_id}/reject", response_model=OutreachResponse)
def reject_outreach(
    outreach_id: int,
    db: Session = Depends(get_db),
):
    record = get_outreach_or_404(outreach_id, db)

    if record.status not in ("draft", "approved"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft or approved outreach records can be rejected.",
        )

    record.status = "rejected"

    commit_changes(db)
    db.refresh(record)

    return record
