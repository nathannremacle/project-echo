"""
Integration tests for health check endpoint
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_health_endpoint_accessible(client):
    """Test that health endpoint is accessible"""
    response = client.get("/health")
    
    assert response.status_code in [200, 503]  # Can be healthy or unhealthy
    assert "status" in response.json()
    assert "checks" in response.json()
    assert "timestamp" in response.json()
    assert "version" in response.json()


def test_health_endpoint_structure(client):
    """Test health endpoint response structure"""
    response = client.get("/health")
    data = response.json()
    
    # Check overall structure
    assert "status" in data
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert "timestamp" in data
    assert "version" in data
    assert "checks" in data
    
    # Check individual component checks
    checks = data["checks"]
    assert "database" in checks
    assert "github_actions" in checks
    assert "dependencies" in checks
    assert "configuration" in checks
    
    # Check component structure
    for check_name, check_data in checks.items():
        assert "status" in check_data
        assert check_data["status"] in ["ok", "error"]
        assert "message" in check_data


def test_health_endpoint_status_codes(client):
    """Test health endpoint returns correct status codes"""
    response = client.get("/health")
    data = response.json()
    
    if data["status"] == "healthy":
        assert response.status_code == 200
    else:
        assert response.status_code == 503


def test_health_endpoint_graceful_errors(client):
    """Test that health endpoint handles errors gracefully"""
    # Even if components fail, endpoint should return valid JSON
    response = client.get("/health")
    
    assert response.status_code in [200, 503]
    assert response.headers["content-type"] == "application/json"
    
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
