"""
Test Human Approval Workflow, Transitions, and Audit Logging
"""

import pytest


def test_draft_cannot_be_ready_without_approval(client):
    """Verifies that newly created tickets cannot automatically have READY status."""
    payload = {
        "ticket_id": "APPR-001",
        "customer_message": "General question about the standard support documentation."
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["review_status"] != "READY"
    assert data["approval_status"] == "UNAPPROVED"


def test_valid_approval_updates_state_and_audit(client):
    """Verifies explicit approval updates ticket to READY and creates an audit record."""
    tid = "APPR-002"
    client.post("/tickets", json={
        "ticket_id": tid,
        "customer_message": "Can I receive an itemized receipt for the latest transaction?"
    })

    # Approve the ticket
    approval_payload = {
        "reviewer_identity": "Agent Alex Smith",
        "confirmed": True,
        "notes": "Verified receipt request. Approved draft response."
    }
    approve_res = client.post(f"/tickets/{tid}/approve", json=approval_payload)
    assert approve_res.status_code == 200
    ticket_data = approve_res.json()
    assert ticket_data["review_status"] == "READY"
    assert ticket_data["approval_status"] == "APPROVED"
    assert ticket_data["reviewer_identity"] == "Agent Alex Smith"
    assert ticket_data["approval_timestamp"] is not None

    # Check Audit History
    audit_res = client.get(f"/tickets/{tid}/audit")
    assert audit_res.status_code == 200
    events = audit_res.json()
    assert len(events) >= 2
    # First was CREATED, second is APPROVED
    assert events[0]["action"] == "CREATED"
    assert events[1]["action"] == "APPROVED"
    assert events[1]["new_status"] == "READY"
    assert events[1]["reviewer_identity"] == "Agent Alex Smith"


def test_rejection_requires_reason(client):
    """Verifies rejection requires a non-empty reason and reviewer identity."""
    tid = "REJ-001"
    client.post("/tickets", json={
        "ticket_id": tid,
        "customer_message": "The system crashed while running exports."
    })

    # Try rejecting without reason
    bad_payload = {
        "reviewer_identity": "Agent Alex Smith",
        "rejection_reason": ""
    }
    bad_res = client.post(f"/tickets/{tid}/reject", json=bad_payload)
    assert bad_res.status_code == 422


def test_valid_rejection_updates_state_and_audit(client):
    """Verifies valid rejection updates status to REJECTED with reason recorded."""
    tid = "REJ-002"
    client.post("/tickets", json={
        "ticket_id": tid,
        "customer_message": "Need admin credentials for entire database."
    })

    rej_payload = {
        "reviewer_identity": "Security Lead Brenda",
        "rejection_reason": "High-risk request violates least-privilege policy. Customer must follow escalation form."
    }
    res = client.post(f"/tickets/{tid}/reject", json=rej_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["review_status"] == "REJECTED"
    assert data["approval_status"] == "REJECTED"
    assert data["rejection_reason"] == rej_payload["rejection_reason"]


def test_invalid_state_transition_rejected(client):
    """Verifies that an already APPROVED (READY) ticket cannot be re-approved or rejected without error."""
    tid = "TRANS-001"
    client.post("/tickets", json={
        "ticket_id": tid,
        "customer_message": "Routine question on user profile."
    })

    # Approve
    client.post(f"/tickets/{tid}/approve", json={
        "reviewer_identity": "Agent Alex",
        "confirmed": True
    })

    # Attempt re-approval on already READY ticket
    re_approve = client.post(f"/tickets/{tid}/approve", json={
        "reviewer_identity": "Agent Alex",
        "confirmed": True
    })
    assert re_approve.status_code == 400
    assert "cannot approve" in re_approve.json()["detail"].lower()

    # Attempt reject on already READY ticket
    re_reject = client.post(f"/tickets/{tid}/reject", json={
        "reviewer_identity": "Agent Alex",
        "rejection_reason": "Trying to reject after ready."
    })
    assert re_reject.status_code == 400
