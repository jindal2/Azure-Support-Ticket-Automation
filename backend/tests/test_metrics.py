"""
Test Dashboard Aggregate Metrics
"""

def test_metrics_endpoint_counts(client):
    """Verifies that GET /metrics accurately computes and aggregates database counts."""
    # Seed known set of tickets
    client.post("/tickets", json={"ticket_id": "MTR-01", "customer_message": "Charged twice on credit card subscription."})
    client.post("/tickets", json={"ticket_id": "MTR-02", "customer_message": "Application crashes on PDF export."})
    client.post("/tickets", json={"ticket_id": "MTR-03", "customer_message": "Where is the API documentation?"})

    # Approve one ticket
    client.post("/tickets/MTR-01/approve", json={"reviewer_identity": "Lead Agent", "confirmed": True})

    # Fetch metrics
    res = client.get("/metrics")
    assert res.status_code == 200
    data = res.json()

    assert data["total_tickets"] == 3
    assert data["approved_count"] == 1
    assert data["rejected_count"] == 0
    assert "categories" in data
    assert "priorities" in data
    assert "review_statuses" in data
    assert data["review_statuses"]["READY"] == 1
