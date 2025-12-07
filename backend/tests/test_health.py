"""
Tests for Health Check Endpoint
"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check_basic(test_client: AsyncClient):
    """Test basic health check"""
    response = await test_client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_health_check_detailed(test_client: AsyncClient):
    """Test detailed health check"""
    response = await test_client.get("/api/health?detailed=true")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check top-level fields
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data
    
    # Check components
    if "components" in data:
        components = data["components"]
        assert "database" in components
        assert "system" in components
        assert "cache" in components

@pytest.mark.asyncio
async def test_health_check_response_time(test_client: AsyncClient):
    """Test health check response time"""
    import time
    
    start_time = time.time()
    response = await test_client.get("/api/health")
    elapsed_time = time.time() - start_time
    
    assert response.status_code == 200
    assert elapsed_time < 1.0  # Should respond in less than 1 second
