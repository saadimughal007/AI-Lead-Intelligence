
from fastapi import FastAPI, HTTPException

from app.database import check_database_connection
from app.models import Lead, Outreach, User
from app.routes.auth import router as auth_router
from app.routes.leads import router as leads_router
from app.routes.outreach import router as outreach_router


app = FastAPI(
    title="AI Lead Intelligence API",
    description="AI-powered lead intelligence and sales automation platform",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(leads_router)
app.include_router(outreach_router)


@app.get("/")
def home():
    return {
        "message": "AI Lead Intelligence API is running!",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/db-check")
def database_health():
    if not check_database_connection():
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )

    return {
        "status": "connected",
        "database": "PostgreSQL",
    }
