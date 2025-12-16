import pytest
from fastapi.testclient import TestClient
from api.server import app

client = TestClient(app)

def test_health_check():
    """Verify API is online."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_recommendation_endpoint():
    """Verify product recommendation logic."""
    payload = {"query": "SICK sensor"}
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "source_documents" in data

def test_quotation_creation():
    """Verify PDF quotation generation."""
    payload = {
        "customer_name": "Test User",
        "customer_email": "test@example.com",
        "items": [
            {"sku": "123", "name": "Test Product", "qty": 1, "price": 100.0}
        ]
    }
    response = client.post("/api/v1/quotations", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
