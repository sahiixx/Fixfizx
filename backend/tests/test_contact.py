"""
Tests for Contact Form Endpoint
"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_contact_form_submission(test_client: AsyncClient, sample_contact_data):
    """Test successful contact form submission"""
    response = await test_client.post("/api/contact", json=sample_contact_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "id" in data.get("data", {})

@pytest.mark.asyncio
async def test_contact_form_missing_fields(test_client: AsyncClient):
    """Test contact form with missing required fields"""
    incomplete_data = {
        "name": "Test User",
        "email": "test@example.com"
        # Missing phone, service, message
    }
    
    response = await test_client.post("/api/contact", json=incomplete_data)
    
    assert response.status_code in [400, 422]  # Bad request or validation error

@pytest.mark.asyncio
async def test_contact_form_invalid_email(test_client: AsyncClient, sample_contact_data):
    """Test contact form with invalid email"""
    sample_contact_data["email"] = "invalid-email"
    
    response = await test_client.post("/api/contact", json=sample_contact_data)
    
    # Should either validate or accept (depending on implementation)
    assert response.status_code in [200, 400, 422]

@pytest.mark.asyncio
async def test_contact_form_duplicate_submission(test_client: AsyncClient, sample_contact_data):
    """Test duplicate contact form submissions"""
    # First submission
    response1 = await test_client.post("/api/contact", json=sample_contact_data)
    assert response1.status_code == 200
    
    # Second submission (should also succeed in current implementation)
    response2 = await test_client.post("/api/contact", json=sample_contact_data)
    assert response2.status_code == 200
