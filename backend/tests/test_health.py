"""
Test Health Check Endpoint
"""

def test_health_endpoint_success(client):
    """Verifies that GET /health returns HTTP 200 with healthy database and classifier status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["classifier"] == "ready"
    assert "version" in data
    assert "timestamp" in data


def test_api_prefixed_health_endpoint(client):
    """Verifies that GET /api/health also returns HTTP 200."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
