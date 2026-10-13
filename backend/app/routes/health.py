"""
Support Ticket Automation System
Health Check Route
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import APP_VERSION
from app.schemas import HealthResponse
from app.models import utc_now
from app.classifier import get_classifier

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Returns system operational health, application version, database connectivity,
    and machine learning classifier availability.
    """
    # Check Database connection
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check Classifier
    clf = get_classifier()
    clf_status = "ready" if clf.is_trained else "not_trained"

    overall_status = "healthy" if (db_status == "connected" and clf_status == "ready") else "degraded"

    return {
        "status": overall_status,
        "version": APP_VERSION,
        "database": db_status,
        "classifier": clf_status,
        "timestamp": utc_now()
    }
