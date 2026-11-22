
from app.services.lead_scoring import score_lead


sample_lead = {
    "full_name": "Ali Khan",
    "email": "ali@example.com",
    "company": "Tech Solutions",
    "website": "https://example.com",
    "job_title": "Marketing Manager",
    "industry": "Software",
    "country": "Pakistan",
    "lead_source": "Manual",
    "status": "qualified",
    "notes": "Interested in marketing automation."
}


if __name__ == "__main__":
    print("\nRunning AI Lead Scoring...\n")

    result = score_lead(sample_lead)

    print("AI LEAD INTELLIGENCE RESULT")
    print("---------------------------")
    print(f"Score: {result['score']}/100")
    print(f"Category: {result['category']}")
    print(f"ICP Match: {result['icp_match']}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"Recommended Action: {result['recommended_action']}")

