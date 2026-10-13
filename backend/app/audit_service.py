"""
Support Ticket Automation System
Audit Logging Service
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import AuditLogModel, utc_now


class AuditService:
    """
    Manages recording and querying the immutable audit history for tickets.
    """

    @staticmethod
    def record_event(
        db: Session,
        ticket_id: str,
        action: str,
        new_status: str,
        previous_status: Optional[str] = None,
        reviewer_identity: Optional[str] = None,
        action_reason: Optional[str] = None
    ) -> AuditLogModel:
        """
        Creates and appends an audit event to the database.
        """
        event = AuditLogModel(
            ticket_id=ticket_id,
            action=action,
            previous_status=previous_status,
            new_status=new_status,
            reviewer_identity=reviewer_identity,
            action_reason=action_reason,
            timestamp=utc_now()
        )
        db.add(event)
        # We do not commit immediately to allow the calling business transaction
        # to commit atomically with the ticket record update.
        return event

    @staticmethod
    def get_audit_trail(db: Session, ticket_id: str) -> List[AuditLogModel]:
        """
        Retrieves the chronological audit events for a given ticket.
        """
        return (
            db.query(AuditLogModel)
            .filter(AuditLogModel.ticket_id == ticket_id)
            .order_by(AuditLogModel.timestamp.asc())
            .all()
        )
