"""
Support Ticket Automation System
Approvals & Audit Trail Routes
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ApprovalRequest, RejectionRequest, TicketResponse, AuditLogResponse
from app.ticket_service import TicketService
from app.audit_service import AuditService

router = APIRouter(prefix="/tickets", tags=["Approvals & Audit"])


@router.post("/{ticket_id}/approve", response_model=TicketResponse)
def approve_ticket_draft(
    ticket_id: str,
    request: ApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    Explicitly approves a ticket response draft, transitioning status to READY.
    Mandates reviewer identity and confirmation boolean in request body.
    Invalid transitions return HTTP 400.
    """
    return TicketService.approve_ticket(db=db, ticket_id=ticket_id, request=request)


@router.post("/{ticket_id}/reject", response_model=TicketResponse)
def reject_ticket_draft(
    ticket_id: str,
    request: RejectionRequest,
    db: Session = Depends(get_db)
):
    """
    Rejects a ticket response draft, transitioning status to REJECTED.
    Mandates a detailed rejection reason and reviewer identity.
    Invalid transitions return HTTP 400.
    """
    return TicketService.reject_ticket(db=db, ticket_id=ticket_id, request=request)


@router.get("/{ticket_id}/audit", response_model=List[AuditLogResponse])
def get_ticket_audit_trail(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns the chronological audit trail for a ticket.
    Returns HTTP 404 if ticket does not exist.
    """
    # Verify ticket exists first
    TicketService.get_ticket(db=db, ticket_id=ticket_id)
    return AuditService.get_audit_trail(db=db, ticket_id=ticket_id)
