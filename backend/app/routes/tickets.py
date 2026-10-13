"""
Support Ticket Automation System
Tickets Processing Routes
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import TicketCreateRequest, TicketResponse, TicketListResponse
from app.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    request: TicketCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Submits a new support ticket.
    Triggers ML classification, priority determination, support team routing,
    extractive summarization, draft generation, and human review gating.
    Rejects duplicates with HTTP 409 and malformed values with HTTP 422.
    """
    return TicketService.create_ticket(db=db, request=request)


@router.get("", response_model=TicketListResponse)
def list_tickets(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=200, description="Page limit"),
    search: Optional[str] = Query(None, description="Search ticket ID or message"),
    category: Optional[str] = Query(None, description="Filter by category (Billing, Technical, Access, General)"),
    priority: Optional[str] = Query(None, description="Filter by priority (CRITICAL, HIGH, MEDIUM, LOW)"),
    review_status: Optional[str] = Query(None, description="Filter by status (PENDING_REVIEW, NEEDS_REVIEW, READY, REJECTED)"),
    db: Session = Depends(get_db)
):
    """
    Lists support tickets with multi-criteria filtering, search, and pagination.
    """
    items, total = TicketService.list_tickets(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        priority=priority,
        review_status=review_status
    )
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket_details(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves full details of a single ticket by its unique ticket ID.
    Returns HTTP 404 if ticket does not exist.
    """
    return TicketService.get_ticket(db=db, ticket_id=ticket_id)
