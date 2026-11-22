from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Outreach(Base):
    __tablename__ = "outreach"

    __table_args__ = (
        CheckConstraint(
            "channel IN ('email', 'linkedin')",
            name="check_outreach_channel",
        ),
        CheckConstraint(
            "message_type IN ('email', 'linkedin_connection', "
            "'linkedin_first_message', 'linkedin_followup')",
            name="check_outreach_message_type",
        ),
        CheckConstraint(
            "status IN ('draft', 'approved', 'rejected', 'sent')",
            name="check_outreach_status",
        ),
        Index("ix_outreach_lead_id", "lead_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    message_type: Mapped[str] = mapped_column(String(40), nullable=False)
    tone: Mapped[str] = mapped_column(
        String(30), default="professional", nullable=False
    )
    subject: Mapped[str | None] = mapped_column(String(300), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    call_to_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="draft", nullable=False
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )