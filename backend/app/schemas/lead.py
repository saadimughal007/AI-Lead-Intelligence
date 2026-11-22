
from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class LeadCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr

    company: str | None = Field(default=None, max_length=150)
    website: str | None = Field(default=None, max_length=255)
    job_title: str | None = Field(default=None, max_length=150)
    industry: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)

    lead_source: str | None = Field(default=None, max_length=100)
    status: str = Field(default="new", max_length=50)
    notes: str | None = None


class LeadUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    email: EmailStr | None = None

    company: str | None = Field(default=None, max_length=150)
    website: str | None = Field(default=None, max_length=255)
    job_title: str | None = Field(default=None, max_length=150)
    industry: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)

    lead_source: str | None = Field(default=None, max_length=100)
    status: str | None = Field(default=None, max_length=50)
    notes: str | None = None


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str

    company: str | None
    website: str | None
    job_title: str | None
    industry: str | None
    country: str | None
    lead_source: str | None
    status: str

    # AI Scoring
    ai_score: float | None
    ai_category: str | None
    icp_match: bool | None
    ai_reasoning: str | None
    recommended_action: str | None
    ai_confidence: int | None
    missing_information: list[str] | None
    score_breakdown: dict[str, Any] | None

    # Company Enrichment
    company_description: str | None
    company_services: list[str] | None
    target_audience: str | None
    business_model: str | None
    enrichment_status: str | None
    enrichment_source_url: str | None
    enrichment_confidence: int | None
    enrichment_notes: str | None
    enrichment_evidence: list[str] | None
    enriched_at: datetime | None

    notes: str | None
    created_at: datetime
    updated_at: datetime
