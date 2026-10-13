"""
Support Ticket Automation System
Dashboard Metrics Route
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import MetricsResponse
from app.ticket_service import TicketService

router = APIRouter(tags=["Metrics"])


@router.get("/metrics", response_model=MetricsResponse)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Returns aggregate counts by category, priority, review status,
    and approval / rejection metrics for dashboard visualization.
    """
    return TicketService.get_metrics(db=db)
