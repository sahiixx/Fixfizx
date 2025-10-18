"""
Unit tests for backend/integrations/stripe_integration.py
Tests Stripe payment integration functionality
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import os
from backend.integrations.stripe_integration import StripeIntegration, stripe_integration


class TestStripeIntegration:
    """Test suite for Stripe payment integration"""
    
    @pytest.fixture
    def integration(self):
        """Create a Stripe integration instance for testing"""
        with patch.dict(os.environ, {'STRIPE_API_KEY': 'sk_test_12345'}):
            return StripeIntegration()
    
    def test_initialization(self, integration):
        """Test initialization with API key"""
        assert integration.api_key == 'sk_test_12345'
        assert integration.stripe_checkout is None
        assert integration.PACKAGES is not None
        
    def test_default_api_key(self):
        """Test default API key when not provided"""
        with patch.dict(os.environ, {}, clear=True):
            integration = StripeIntegration()
            assert integration.api_key == 'sk_test_emergent'
    
    def test_payment_packages_configuration(self, integration):
        """Test payment packages are properly configured"""
        assert "starter" in integration.PACKAGES
        assert "growth" in integration.PACKAGES
        assert "enterprise" in integration.PACKAGES
        
        # Check starter package
        starter = integration.PACKAGES["starter"]
        assert starter["amount"] == 2500.00
        assert starter["currency"] == "aed"
        assert "name" in starter
        
    def test_all_packages_have_required_fields(self, integration):
        """Test all packages have required fields"""
        for _package_id, package in integration.PACKAGES.items():
            assert "amount" in package
            assert "currency" in package
            assert "name" in package
            assert package["amount"] > 0
            
    def test_initialize_method(self, integration):
        """Test initialize method sets up checkout"""
        webhook_url = "https://example.com/webhook"
        
        with patch('backend.integrations.stripe_integration.StripeCheckout') as mock_checkout:
            integration.initialize(webhook_url)
            
            mock_checkout.assert_called_once_with(
                api_key=integration.api_key,
                webhook_url=webhook_url
            )
            assert integration.stripe_checkout is not None
    
    @pytest.mark.asyncio
    async def test_create_session_invalid_package(self, integration):
        """Test creating session with invalid package ID"""
        result = await integration.create_session(
            package_id="invalid_package",
            host_url="https://example.com"
        )
        
        assert "error" in result
        assert result["error"] == "Invalid package"
    
    @pytest.mark.asyncio
    @patch('backend.integrations.stripe_integration.StripeCheckout')
    async def test_create_session_success(self, mock_checkout_class):
        """Test successful checkout session creation"""
        # Mock session response
        mock_session = Mock()
        mock_session.url = "https://checkout.stripe.com/session123"
        mock_session.session_id = "cs_test_123"
        
        mock_checkout_instance = AsyncMock()
        mock_checkout_instance.create_checkout_session = AsyncMock(return_value=mock_session)
        mock_checkout_class.return_value = mock_checkout_instance
        
        integration = StripeIntegration()
        integration.stripe_checkout = mock_checkout_instance
        
        result = await integration.create_session(
            package_id="starter",
            host_url="https://example.com",
            metadata={"user_id": "123"}
        )
        
        assert "url" in result
        assert result["url"] == "https://checkout.stripe.com/session123"
        assert result["session_id"] == "cs_test_123"
        assert "package" in result
        
    @pytest.mark.asyncio
    @patch('backend.integrations.stripe_integration.StripeCheckout')
    async def test_create_session_initializes_checkout(self, mock_checkout_class):
        """Test that create_session initializes checkout if not already done"""
        mock_session = Mock()
        mock_session.url = "https://checkout.stripe.com/session"
        mock_session.session_id = "cs_test"
        
        mock_checkout_instance = AsyncMock()
        mock_checkout_instance.create_checkout_session = AsyncMock(return_value=mock_session)
        mock_checkout_class.return_value = mock_checkout_instance
        
        integration = StripeIntegration()
        
        result = await integration.create_session(
            package_id="growth",
            host_url="https://example.com"
        )
        
        assert integration.stripe_checkout is not None
        assert "url" in result
        
    @pytest.mark.asyncio
    async def test_create_session_with_all_packages(self, integration):
        """Test creating sessions for all available packages"""
        mock_session = Mock()
        mock_session.url = "https://checkout.stripe.com/session"
        mock_session.session_id = "cs_test"
        
        mock_checkout = AsyncMock()
        mock_checkout.create_checkout_session = AsyncMock(return_value=mock_session)
        integration.stripe_checkout = mock_checkout
        
        for package_id in ["starter", "growth", "enterprise"]:
            result = await integration.create_session(
                package_id=package_id,
                host_url="https://example.com"
            )
            
            assert "url" in result
            assert "session_id" in result
            assert "package" in result
            assert result["package"]["name"]
    
    @pytest.mark.asyncio
    @patch('backend.integrations.stripe_integration.StripeCheckout')
    async def test_create_session_with_metadata(self, mock_checkout_class):
        """Test creating session with custom metadata"""
        mock_session = Mock()
        mock_session.url = "https://checkout.stripe.com/session"
        mock_session.session_id = "cs_test"
        
        mock_checkout_instance = AsyncMock()
        mock_checkout_instance.create_checkout_session = AsyncMock(return_value=mock_session)
        mock_checkout_class.return_value = mock_checkout_instance
        
        integration = StripeIntegration()
        integration.stripe_checkout = mock_checkout_instance
        
        metadata = {
            "user_id": "user_123",
            "tenant_id": "tenant_456",
            "plan_type": "annual"
        }
        
        result = await integration.create_session(
            package_id="enterprise",
            host_url="https://example.com",
            metadata=metadata
        )
        
        assert "url" in result
        
    @pytest.mark.asyncio
    async def test_create_session_error_handling(self, integration):
        """Test error handling in session creation"""
        mock_checkout = AsyncMock()
        mock_checkout.create_checkout_session = AsyncMock(
            side_effect=Exception("Stripe API Error")
        )
        integration.stripe_checkout = mock_checkout
        
        result = await integration.create_session(
            package_id="starter",
            host_url="https://example.com"
        )
        
        assert "error" in result
        assert "Stripe API Error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_status_success(self, integration):
        """Test getting checkout status successfully"""
        mock_status = Mock()
        mock_status.status = "complete"
        mock_status.payment_status = "paid"
        mock_status.amount_total = 250000  # in cents
        mock_status.currency = "aed"
        
        mock_checkout = AsyncMock()
        mock_checkout.get_checkout_status = AsyncMock(return_value=mock_status)
        integration.stripe_checkout = mock_checkout
        
        result = await integration.get_status("cs_test_123")
        
        assert result["status"] == "complete"
        assert result["payment_status"] == "paid"
        assert result["amount_total"] == 250000
        assert result["currency"] == "aed"
    
    @pytest.mark.asyncio
    async def test_get_status_error(self, integration):
        """Test error handling in get_status"""
        mock_checkout = AsyncMock()
        mock_checkout.get_checkout_status = AsyncMock(
            side_effect=Exception("Session not found")
        )
        integration.stripe_checkout = mock_checkout
        
        result = await integration.get_status("invalid_session")
        
        assert "error" in result
        assert "Session not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_status_pending_payment(self, integration):
        """Test getting status for pending payment"""
        mock_status = Mock()
        mock_status.status = "open"
        mock_status.payment_status = "unpaid"
        mock_status.amount_total = 500000
        mock_status.currency = "aed"
        
        mock_checkout = AsyncMock()
        mock_checkout.get_checkout_status = AsyncMock(return_value=mock_status)
        integration.stripe_checkout = mock_checkout
        
        result = await integration.get_status("cs_pending")
        
        assert result["status"] == "open"
        assert result["payment_status"] == "unpaid"
    
    def test_package_amounts_are_in_aed(self, integration):
        """Test that all package amounts are in AED currency"""
        for package in integration.PACKAGES.values():
            assert package["currency"] == "aed"
    
    def test_package_amounts_are_reasonable(self, integration):
        """Test that package amounts are within reasonable ranges"""
        starter = integration.PACKAGES["starter"]["amount"]
        growth = integration.PACKAGES["growth"]["amount"]
        enterprise = integration.PACKAGES["enterprise"]["amount"]
        
        # Check that pricing tiers make sense
        assert starter < growth < enterprise
        assert starter >= 1000  # At least 1000 AED
        assert enterprise <= 50000  # Not more than 50000 AED
    
    def test_global_stripe_integration_instance(self):
        """Test global integration instance exists"""
        assert stripe_integration is not None
        assert isinstance(stripe_integration, StripeIntegration)