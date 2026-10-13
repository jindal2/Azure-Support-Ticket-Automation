"""
Test Ticket Ingestion, Validation, and Retrieval
"""

import pytest


def test_create_valid_billing_ticket(client):
    """Verifies that a valid billing ticket is processed and created with HTTP 201."""
    payload = {
        "ticket_id": "TEST-BILL-101",
        "customer_message": "I was charged twice on my credit card for the monthly subscription."
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["ticket_id"] == "TEST-BILL-101"
    assert data["predicted_category"] == "Billing"
    assert data["assigned_team"] == "Billing Support"
    assert data["review_status"] in ["PENDING_REVIEW", "NEEDS_REVIEW"]
    assert data["approval_status"] == "UNAPPROVED"
    assert len(data["summary"]) > 0
    assert len(data["draft_response"]) > 0


def test_create_valid_technical_ticket(client):
    """Verifies that a technical defect ticket is processed and created with HTTP 201."""
    payload = {
        "ticket_id": "TEST-TECH-101",
        "customer_message": "The application crashes whenever I upload a PDF."
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["ticket_id"] == "TEST-TECH-101"
    assert data["predicted_category"] == "Technical"
    assert data["assigned_team"] == "Technical Support"


def test_duplicate_ticket_id_returns_409(client):
    """Verifies that submitting a duplicate ticket ID returns HTTP 409 Conflict."""
    payload = {
        "ticket_id": "DUP-001",
        "customer_message": "First ticket message regarding access issues."
    }
    res1 = client.post("/tickets", json=payload)
    assert res1.status_code == 201

    # Second submission with same ID
    res2 = client.post("/tickets", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_missing_ticket_id_rejected(client):
    """Verifies that a payload without ticket_id returns HTTP 422."""
    payload = {
        "customer_message": "Some valid message without a ticket ID."
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 422


def test_empty_message_rejected(client):
    """Verifies that an empty message string is rejected with HTTP 422."""
    payload = {
        "ticket_id": "EMPTY-001",
        "customer_message": ""
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 422


def test_whitespace_only_message_rejected(client):
    """Verifies that a whitespace-only message is rejected with HTTP 422."""
    payload = {
        "ticket_id": "WHITE-001",
        "customer_message": "   \n\t   "
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 422


def test_nonexistent_ticket_returns_404(client):
    """Verifies that retrieving a nonexistent ticket ID returns HTTP 404."""
    response = client.get("/tickets/NONEXISTENT-999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_critical_outage_ticket_requires_review(client):
    """Verifies that a ticket describing widespread outage is assigned NEEDS_REVIEW."""
    payload = {
        "ticket_id": "CRIT-TEST-001",
        "customer_message": "Critical outage: Complete system down for all users with 500 error."
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["priority"] == "CRITICAL"
    assert data["review_status"] == "NEEDS_REVIEW"


def test_list_and_filter_tickets(client):
    """Verifies list filtering by category and search."""
    # Seed 2 tickets
    client.post("/tickets", json={"ticket_id": "LST-01", "customer_message": "Billing question on invoice 123."})
    client.post("/tickets", json={"ticket_id": "LST-02", "customer_message": "Cannot login password reset failed."})

    res = client.get("/tickets")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 2

    # Search filter
    search_res = client.get("/tickets?search=invoice")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert any(item["ticket_id"] == "LST-01" for item in search_data["items"])
