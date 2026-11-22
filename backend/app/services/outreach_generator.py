
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.services.gemini import client


class GeneratedDraft(BaseModel):
    model_config = ConfigDict(extra="ignore")

    channel: Literal["email", "linkedin"]
    message_type: Literal[
        "email",
        "linkedin_connection",
        "linkedin_first_message",
        "linkedin_followup",
    ]
    subject: str | None = Field(default=None, max_length=300)
    message: str = Field(min_length=5, max_length=10000)
    call_to_action: str | None = Field(default=None, max_length=1000)


class GeneratedDraftCollection(BaseModel):
    model_config = ConfigDict(extra="ignore")

    drafts: list[GeneratedDraft] = Field(min_length=4, max_length=4)


def generate_outreach_drafts(lead: dict, options: dict) -> list[dict]:
    lead_context = {
        key: value
        for key, value in lead.items()
        if value is not None
    }

    prompt = f"""
You are an expert B2B sales outreach copywriter.

Generate exactly FOUR personalized outreach drafts using the
lead information and sender instructions below.

LEAD INFORMATION:
{json.dumps(lead_context, indent=2, default=str)}

SENDER INSTRUCTIONS:
{json.dumps(options, indent=2, default=str)}

REQUIRED OUTPUT:
Return one JSON object with a "drafts" array containing exactly
these four drafts in this exact order:

1. Email:
   channel = "email"
   message_type = "email"
   Include a relevant subject.
   Write approximately 90-150 words.

2. LinkedIn connection request:
   channel = "linkedin"
   message_type = "linkedin_connection"
   Message must not exceed 300 characters.

3. LinkedIn first message:
   channel = "linkedin"
   message_type = "linkedin_first_message"
   Write a personalized introductory message.

4. LinkedIn follow-up:
   channel = "linkedin"
   message_type = "linkedin_followup"
   Write a polite follow-up message.

Each draft must contain:
- channel
- message_type
- subject (null if not applicable)
- message
- call_to_action (null if not applicable)

IMPORTANT RULES:
- Use only facts present in the lead information.
- Never invent company achievements, statistics, or relationships.
- Personalize messages using available company and lead details.
- Keep language natural, professional, and concise.
- Follow the requested tone and goal.
- Do not include markdown or explanations.
- Return valid JSON only.

EXPECTED JSON STRUCTURE:
{{
  "drafts": [
    {{
      "channel": "email",
      "message_type": "email",
      "subject": "Example subject",
      "message": "Example message",
      "call_to_action": "Example CTA"
    }},
    {{
      "channel": "linkedin",
      "message_type": "linkedin_connection",
      "subject": null,
      "message": "Example connection message",
      "call_to_action": null
    }},
    {{
      "channel": "linkedin",
      "message_type": "linkedin_first_message",
      "subject": null,
      "message": "Example first message",
      "call_to_action": "Example CTA"
    }},
    {{
      "channel": "linkedin",
      "message_type": "linkedin_followup",
      "subject": null,
      "message": "Example follow-up",
      "call_to_action": "Example CTA"
    }}
  ]
}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
        },
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    try:
        parsed = GeneratedDraftCollection.model_validate_json(
            response.text
        )
    except ValidationError as error:
        raise ValueError(
            f"Gemini returned an invalid outreach structure: {error}"
        ) from error

    expected = [
        ("email", "email"),
        ("linkedin", "linkedin_connection"),
        ("linkedin", "linkedin_first_message"),
        ("linkedin", "linkedin_followup"),
    ]

    actual = [
        (draft.channel, draft.message_type)
        for draft in parsed.drafts
    ]

    if actual != expected:
        raise ValueError(
            f"Unexpected draft types. Expected {expected}, received {actual}"
        )

    connection_draft = parsed.drafts[1]

    if len(connection_draft.message) > 300:
        raise ValueError(
            "LinkedIn connection request exceeds 300 characters."
        )

    if not parsed.drafts[0].subject:
        raise ValueError("Email subject is required.")

    return [
        draft.model_dump()
        for draft in parsed.drafts
    ]
