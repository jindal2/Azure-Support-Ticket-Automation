"""
Support Ticket Automation System
Database Models (SQLAlchemy ORM)
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now() -> datetime:
    """Helper returning current UTC datetime."""
    return datetime.now(timezone.utc)


class TicketModel(Base):
    """
    Primary database entity storing support tickets and their AI analysis.
    """
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(String(64), unique=True, index=True, nullable=False)
    customer_message = Column(Text, nullable=False)
    predicted_category = Column(String(32), nullable=False, index=True)
    priority = Column(String(16), nullable=False, index=True)
    assigned_team = Column(String(64), nullable=False)
    summary = Column(Text, nullable=False)
    draft_response = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)

    # Review & Approval Lifecycle:
    # review_status: PENDING_REVIEW, NEEDS_REVIEW, READY, REJECTED
    # approval_status: UNAPPROVED, APPROVED, REJECTED
    review_status = Column(String(32), nullable=False, default="PENDING_REVIEW", index=True)
    approval_status = Column(String(32), nullable=False, default="UNAPPROVED", index=True)

    reviewer_identity = Column(String(128), nullable=True)
    approval_timestamp = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationship to audit logs
    audit_logs = relationship("AuditLogModel", back_populates="ticket", cascade="all, delete-orphan", order_by="AuditLogModel.timestamp.asc()")


class AuditLogModel(Base):
    """
    Immutable chronological audit trail recording ticket lifecycle actions and reviews.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(String(64), ForeignKey("tickets.ticket_id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(32), nullable=False)  # CREATED, APPROVED, REJECTED
    previous_status = Column(String(32), nullable=True)
    new_status = Column(String(32), nullable=False)
    reviewer_identity = Column(String(128), nullable=True)
    action_reason = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utc_now, nullable=False)

    ticket = relationship("TicketModel", back_populates="audit_logs")
