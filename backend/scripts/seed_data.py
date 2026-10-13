"""
Support Ticket Automation System
Database Seeder Script

Seeds the database with representative support tickets for demonstration:
- Standard clear tickets (Billing, Technical, Access, General)
- Ambiguous multi-domain ticket
- Widespread outage critical ticket
- Suspected security incident critical ticket

Usage:
    python backend/scripts/seed_data.py
"""

import sys
import json
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal, init_db
from app.ticket_service import TicketService
from app.schemas import TicketCreateRequest, ApprovalRequest, RejectionRequest


def seed_database():
    print("Initializing database tables...")
    init_db()

    samples_path = backend_dir / "sample_data" / "sample_requests.json"
    if not samples_path.exists():
        print(f"Error: {samples_path} does not exist.")
        sys.exit(1)

    with open(samples_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    db = SessionLocal()
    created_count = 0
    skipped_count = 0

    print(f"Seeding {len(samples)} demonstration tickets...")

    for item in samples:
        tid = item["ticket_id"]
        msg = item["customer_message"]

        try:
            req = TicketCreateRequest(ticket_id=tid, customer_message=msg)
            ticket = TicketService.create_ticket(db=db, request=req)
            created_count += 1
            print(f"  [+] Created ticket '{tid}': Category='{ticket.predicted_category}', Priority='{ticket.priority}', Status='{ticket.review_status}'")
        except Exception as e:
            skipped_count += 1
            print(f"  [-] Skipped ticket '{tid}' (already exists or error: {e})")

    # Let's also demonstrate a sample approval and a sample rejection if tickets exist
    try:
        # Approve BILL-001 as an example of a reviewed ready ticket
        bill_ticket = TicketService.get_ticket(db, "BILL-001")
        if bill_ticket.review_status != "READY":
            TicketService.approve_ticket(
                db=db,
                ticket_id="BILL-001",
                request=ApprovalRequest(
                    reviewer_identity="Lead Agent Sarah Jenkins",
                    confirmed=True,
                    notes="Verified double billing transaction ID. Approved customer draft."
                )
            )
            print("  [✓] Sample action: Approved BILL-001 to READY status.")
    except Exception as e:
        pass

    try:
        # Reject GEN-001 as an example of a rejected draft requiring revision
        gen_ticket = TicketService.get_ticket(db, "GEN-001")
        if gen_ticket.review_status != "REJECTED":
            TicketService.reject_ticket(
                db=db,
                ticket_id="GEN-001",
                request=RejectionRequest(
                    reviewer_identity="Senior Reviewer Michael Chang",
                    rejection_reason="Customer is asking for Enterprise SLA tier comparison. Need customized quotation template."
                )
            )
            print("  [✗] Sample action: Rejected GEN-001 with documented reason.")
    except Exception as e:
        pass

    db.close()
    print(f"\nDatabase seeding completed! Created: {created_count}, Skipped: {skipped_count}.")


if __name__ == "__main__":
    seed_database()
