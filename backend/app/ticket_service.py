"""
Support Ticket Automation System
Ticket Business Logic & Orchestration Service
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models import TicketModel, utc_now
from app.schemas import TicketCreateRequest, ApprovalRequest, RejectionRequest
from app.classifier import get_classifier
from app.priority_service import evaluate_ticket_priority_and_team, PRIORITY_CRITICAL
from app.response_generator import generate_summary, generate_draft_response
from app.audit_service import AuditService

logger = logging.getLogger("app.ticket_service")


class TicketService:
    """
    Core business service managing support ticket processing, ML classification,
    priority scoring, response drafting, and human approval lifecycles.
    """

    @classmethod
    def create_ticket(cls, db: Session, request: TicketCreateRequest) -> TicketModel:
        """
        Processes and creates a new support ticket:
        1. Validates input and uniqueness.
        2. Executes ML classification pipeline.
        3. Assigns priority and support team.
        4. Synthesizes summary and compliant draft response.
        5. Computes human review status (PENDING_REVIEW or NEEDS_REVIEW).
        6. Persists ticket and writes initial audit record atomically.
        """
        # Preliminary uniqueness check
        existing = db.query(TicketModel).filter(TicketModel.ticket_id == request.ticket_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ticket ID '{request.ticket_id}' already exists in the system."
            )

        # 1. Machine Learning Classification
        classifier = get_classifier()
        clf_result = classifier.predict(request.customer_message)
        predicted_category = clf_result["predicted_category"]
        confidence_score = clf_result["confidence_score"]
        is_uncertain = clf_result["review_recommendation"]

        # 2. Priority & Team Assignment
        priority, assigned_team, priority_meta = evaluate_ticket_priority_and_team(
            request.customer_message,
            predicted_category
        )
        is_critical = priority_meta["is_critical_risk"]
        is_security = priority_meta["is_suspected_security"]

        # 3. Determine Review Status
        # Newly created tickets can NEVER be READY.
        # If critical or ML is uncertain -> NEEDS_REVIEW.
        # Otherwise -> PENDING_REVIEW.
        if is_critical or is_uncertain:
            review_status = "NEEDS_REVIEW"
        else:
            review_status = "PENDING_REVIEW"

        # 4. Generate Truthful Summary & Polite Draft Response
        summary = generate_summary(request.customer_message)
        draft_response = generate_draft_response(
            category=predicted_category,
            priority=priority,
            message=request.customer_message,
            is_uncertain=is_uncertain,
            is_critical=is_critical,
            is_security=is_security,
            ticket_id=request.ticket_id
        )

        ticket = TicketModel(
            ticket_id=request.ticket_id,
            customer_message=request.customer_message,
            predicted_category=predicted_category,
            priority=priority,
            assigned_team=assigned_team,
            summary=summary,
            draft_response=draft_response,
            confidence_score=confidence_score,
            review_status=review_status,
            approval_status="UNAPPROVED",
            reviewer_identity=None,
            approval_timestamp=None,
            rejection_reason=None,
            created_at=utc_now(),
            updated_at=utc_now()
        )

        try:
            db.add(ticket)
            # Create initial audit log event
            action_reason = (
                f"Automated ingestion: Predicted '{predicted_category}' ({confidence_score:.2f} conf), "
                f"Priority '{priority}'. Initial status: '{review_status}'."
            )
            AuditService.record_event(
                db=db,
                ticket_id=ticket.ticket_id,
                action="CREATED",
                new_status=review_status,
                previous_status=None,
                reviewer_identity="SYSTEM_AI_ROUTER",
                action_reason=action_reason
            )
            db.commit()
            db.refresh(ticket)
            return ticket

        except IntegrityError as e:
            db.rollback()
            logger.warning(f"Integrity error creating ticket {request.ticket_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ticket ID '{request.ticket_id}' already exists."
            )
        except Exception as e:
            db.rollback()
            logger.exception(f"Unexpected error creating ticket {request.ticket_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal server error occurred while processing the ticket."
            )

    @classmethod
    def get_ticket(cls, db: Session, ticket_id: str) -> TicketModel:
        """Retrieves a ticket by unique ticket_id, or raises 404."""
        ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with ID '{ticket_id}' not found."
            )
        return ticket

    @classmethod
    def list_tickets(
        cls,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        review_status: Optional[str] = None
    ) -> Tuple[List[TicketModel], int]:
        """Queries tickets with multi-field filtering and pagination."""
        query = db.query(TicketModel)

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                (TicketModel.ticket_id.ilike(search_term)) |
                (TicketModel.customer_message.ilike(search_term)) |
                (TicketModel.summary.ilike(search_term))
            )

        if category:
            query = query.filter(TicketModel.predicted_category == category)

        if priority:
            query = query.filter(TicketModel.priority == priority)

        if review_status:
            query = query.filter(TicketModel.review_status == review_status)

        total = query.count()
        items = query.order_by(TicketModel.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    @classmethod
    def approve_ticket(cls, db: Session, ticket_id: str, request: ApprovalRequest) -> TicketModel:
        """
        Authorizes a ticket draft to READY status.
        Only allows transition from PENDING_REVIEW or NEEDS_REVIEW.
        """
        ticket = cls.get_ticket(db, ticket_id)

        # Enforce valid lifecycle state transition
        if ticket.review_status in ["READY", "REJECTED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot approve ticket with status '{ticket.review_status}'. "
                    f"Only tickets in 'PENDING_REVIEW' or 'NEEDS_REVIEW' can be approved."
                )
            )

        prev_status = ticket.review_status
        now = utc_now()

        ticket.review_status = "READY"
        ticket.approval_status = "APPROVED"
        ticket.reviewer_identity = request.reviewer_identity
        ticket.approval_timestamp = now
        ticket.updated_at = now

        action_reason = request.notes or f"Explicit approval granted by reviewer '{request.reviewer_identity}'."
        AuditService.record_event(
            db=db,
            ticket_id=ticket.ticket_id,
            action="APPROVED",
            previous_status=prev_status,
            new_status="READY",
            reviewer_identity=request.reviewer_identity,
            action_reason=action_reason
        )

        db.commit()
        db.refresh(ticket)
        return ticket

    @classmethod
    def reject_ticket(cls, db: Session, ticket_id: str, request: RejectionRequest) -> TicketModel:
        """
        Rejects a ticket draft, transitioning it to REJECTED.
        Mandates a non-empty rejection reason.
        Only allows transition from PENDING_REVIEW or NEEDS_REVIEW.
        """
        ticket = cls.get_ticket(db, ticket_id)

        if ticket.review_status in ["READY", "REJECTED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot reject ticket with status '{ticket.review_status}'. "
                    f"Only tickets in 'PENDING_REVIEW' or 'NEEDS_REVIEW' can be rejected."
                )
            )

        prev_status = ticket.review_status
        now = utc_now()

        ticket.review_status = "REJECTED"
        ticket.approval_status = "REJECTED"
        ticket.reviewer_identity = request.reviewer_identity
        ticket.rejection_reason = request.rejection_reason
        ticket.updated_at = now

        AuditService.record_event(
            db=db,
            ticket_id=ticket.ticket_id,
            action="REJECTED",
            previous_status=prev_status,
            new_status="REJECTED",
            reviewer_identity=request.reviewer_identity,
            action_reason=f"Rejected: {request.rejection_reason}"
        )

        db.commit()
        db.refresh(ticket)
        return ticket

    @classmethod
    def get_metrics(cls, db: Session) -> Dict[str, Any]:
        """Calculates aggregated metrics for dashboard display."""
        total = db.query(TicketModel).count()

        # Categories
        cat_counts = {"Billing": 0, "Technical": 0, "Access": 0, "General": 0}
        for cat in cat_counts.keys():
            cat_counts[cat] = db.query(TicketModel).filter(TicketModel.predicted_category == cat).count()

        # Priorities
        priority_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for prio in priority_counts.keys():
            priority_counts[prio] = db.query(TicketModel).filter(TicketModel.priority == prio).count()

        # Statuses
        status_counts = {"PENDING_REVIEW": 0, "NEEDS_REVIEW": 0, "READY": 0, "REJECTED": 0}
        for st in status_counts.keys():
            status_counts[st] = db.query(TicketModel).filter(TicketModel.review_status == st).count()

        approved_count = db.query(TicketModel).filter(TicketModel.approval_status == "APPROVED").count()
        rejected_count = db.query(TicketModel).filter(TicketModel.approval_status == "REJECTED").count()

        return {
            "total_tickets": total,
            "categories": cat_counts,
            "priorities": priority_counts,
            "review_statuses": status_counts,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "pending_review_count": status_counts["PENDING_REVIEW"],
            "needs_review_count": status_counts["NEEDS_REVIEW"]
        }
