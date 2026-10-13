"""
Support Ticket Automation System
Pydantic Schemas for Request & Response Validation
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, field_validator, ConfigDict


# -------------------------------------------------------------
# Ticket Schemas
# -------------------------------------------------------------

class TicketCreateRequest(BaseModel):
    """Schema for incoming ticket submission."""
    ticket_id: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Unique business identifier for the support ticket (e.g. BILL-001)"
    )
    customer_message: str = Field(
        ...,
        min_length=1,
        description="Full customer message content"
    )

    @field_validator("ticket_id")
    @classmethod
    def validate_ticket_id(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("ticket_id cannot be empty or whitespace only.")
        return trimmed

    @field_validator("customer_message")
    @classmethod
    def validate_customer_message(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("customer_message cannot be empty or whitespace only.")
        return trimmed


class TicketResponse(BaseModel):
    """Schema for returning ticket details."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: str
    customer_message: str
    predicted_category: str
    priority: str
    assigned_team: str
    summary: str
    draft_response: str
    confidence_score: Optional[float] = None
    review_status: str
    approval_status: str
    reviewer_identity: Optional[str] = None
    approval_timestamp: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TicketListResponse(BaseModel):
    """Paginated ticket listing response."""
    items: List[TicketResponse]
    total: int
    skip: int
    limit: int


# -------------------------------------------------------------
# Approval & Rejection Schemas
# -------------------------------------------------------------

class ApprovalRequest(BaseModel):
    """Schema for human review approval action."""
    reviewer_identity: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Name or email of the human reviewer taking responsibility."
    )
    confirmed: bool = Field(
        ...,
        description="Explicit confirmation boolean authorizing the draft to READY."
    )
    notes: Optional[str] = Field(
        None,
        description="Optional internal review notes."
    )

    @field_validator("reviewer_identity")
    @classmethod
    def validate_reviewer(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("reviewer_identity cannot be empty or blank.")
        return trimmed

    @field_validator("confirmed")
    @classmethod
    def validate_confirmation(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Explicit confirmation must be true to approve a draft.")
        return v


class RejectionRequest(BaseModel):
    """Schema for human review rejection action."""
    reviewer_identity: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Name or email of the reviewer rejecting the draft."
    )
    rejection_reason: str = Field(
        ...,
        min_length=3,
        description="Mandatory clear explanation why the draft was rejected."
    )

    @field_validator("reviewer_identity")
    @classmethod
    def validate_reviewer(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("reviewer_identity cannot be empty or blank.")
        return trimmed

    @field_validator("rejection_reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("rejection_reason must be provided and cannot be blank.")
        return trimmed


# -------------------------------------------------------------
# Audit Log Schemas
# -------------------------------------------------------------

class AuditLogResponse(BaseModel):
    """Schema for audit event response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: str
    action: str
    previous_status: Optional[str] = None
    new_status: str
    reviewer_identity: Optional[str] = None
    action_reason: Optional[str] = None
    timestamp: datetime


# -------------------------------------------------------------
# Health & Metrics Schemas
# -------------------------------------------------------------

class HealthResponse(BaseModel):
    """Schema for system health check."""
    status: str
    version: str
    database: str
    classifier: str
    timestamp: datetime


class MetricsResponse(BaseModel):
    """Schema for dashboard aggregate metrics."""
    total_tickets: int
    categories: Dict[str, int]
    priorities: Dict[str, int]
    review_statuses: Dict[str, int]
    approved_count: int
    rejected_count: int
    pending_review_count: int
    needs_review_count: int
