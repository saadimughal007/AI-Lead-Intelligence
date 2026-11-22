
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    JSON,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    full_name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    company: Mapped[str | None] = mapped_column(
        String(150), nullable=True
    )

    website: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    job_title: Mapped[str | None] = mapped_column(
        String(150), nullable=True
    )

    industry: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    country: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    lead_source: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50), default="new", nullable=False
    )

    # AI Lead Scoring
    ai_score: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    ai_category: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )

    icp_match: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )

    ai_reasoning: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    recommended_action: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    ai_confidence: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    missing_information: Mapped[list | None] = mapped_column(
        JSON, nullable=True
    )

    score_breakdown: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )

    # Company Enrichment
    company_description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    company_services: Mapped[list | None] = mapped_column(
        JSON, nullable=True
    )

    target_audience: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    business_model: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    enrichment_status: Mapped[str | None] = mapped_column(
        String(30), default="pending", nullable=True
    )

    enrichment_source_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    enrichment_confidence: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    enrichment_notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    enrichment_evidence: Mapped[list | None] = mapped_column(
        JSON, nullable=True
    )

    enriched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
