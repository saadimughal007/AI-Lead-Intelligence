
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT.parent / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing from the root .env file")

client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(
        api_version="v1beta"
    ),
)


def test_gemini_connection() -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Reply with exactly: Gemini connection successful."
    )

    return response.text or "Gemini returned an empty response."
