
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Tone = Literal["professional", "friendly", "persuasive"]
OutreachStatus = Literal["draft", "approved", "rejected", "sent"]
OutreachChannel = Literal["email", "linkedin"]


class OutreachGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tone: Tone = "professional"
    goal: str = Field(
        default="Start a relevant business conversation",
        min_length=5,
        max_length=500,
    )
    sender_name: str | None = Field(default=None, max_length=120)
    sender_company: str | None = Field(default=None, max_length=150)
    offering: str | None = Field(default=None, max_length=500)
    additional_context: str | None = Field(default=None, max_length=1500)


class OutreachUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str | None = Field(default=None, max_length=300)
    message: str | None = Field(default=None, min_length=5, max_length=10000)
    call_to_action: str | None = Field(default=None, max_length=1000)
    tone: Tone | None = None

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")

        if "message" in self.model_fields_set and self.message is None:
            raise ValueError("Message cannot be null.")

        if "tone" in self.model_fields_set and self.tone is None:
            raise ValueError("Tone cannot be null.")

        return self


class OutreachResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    channel: str
    message_type: str
    tone: str
    subject: str | None
    message: str
    call_to_action: str | None
    status: str
    generated_at: datetime
    updated_at: datetime
    approved_at: datetime | None
    sent_at: datetime | None
