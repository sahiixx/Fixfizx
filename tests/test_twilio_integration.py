"""
Unit tests for backend/integrations/twilio_integration.py
Tests Twilio SMS and verification functionality
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import os
from backend.integrations.twilio_integration import TwilioIntegration, twilio_integration


class TestTwilioIntegration:
    """Test suite for Twilio SMS integration"""
    
    @pytest.fixture
    def integration(self):
        """Create a Twilio integration instance for testing"""
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'ACtest123456',
            'TWILIO_AUTH_TOKEN': 'test_token',
            'TWILIO_VERIFY_SERVICE': 'VAtest123',
            'TWILIO_PHONE_NUMBER': '+15551234567'
        }):
            with patch('backend.integrations.twilio_integration.Client'):
                return TwilioIntegration()
    
    @pytest.fixture
    def integration_no_creds(self):
        """Create integration without credentials"""
        with patch.dict(os.environ, {}, clear=True):
            return TwilioIntegration()
    
    def test_initialization_with_credentials(self, integration):
        """Test initialization with valid credentials"""
        assert integration.account_sid == 'ACtest123456'
        assert integration.auth_token == 'test_token'  # noqa: S105
        assert integration.verify_service_sid == 'VAtest123'
        
    def test_initialization_without_credentials(self, integration_no_creds):
        """Test initialization without credentials"""
        assert integration_no_creds.account_sid is None
        assert integration_no_creds.auth_token is None
        assert integration_no_creds.client is None
        
    @pytest.mark.asyncio
    async def test_send_otp_without_client(self, integration_no_creds):
        """Test sending OTP when client is not configured"""
        result = await integration_no_creds.send_otp("+971501234567")
        
        assert "error" in result
        assert result["error"] == "Twilio not configured"
        assert result.get("test_mode") is True
        
    @pytest.mark.asyncio
    @patch('backend.integrations.twilio_integration.Client')
    async def test_send_otp_success(self, mock_client_class):
        """Test successful OTP sending"""
        mock_verification = Mock()
        mock_verification.status = "pending"
        
        mock_verify = Mock()
        mock_verify.verifications = Mock()
        mock_verify.verifications.create = Mock(return_value=mock_verification)
        
        mock_verify_service = Mock()
        mock_verify_service.services = Mock(return_value=mock_verify)
        
        mock_client = Mock()
        mock_client.verify = mock_verify_service
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'ACtest',
            'TWILIO_AUTH_TOKEN': 'token',
            'TWILIO_VERIFY_SERVICE': 'VAtest'
        }):
            integration = TwilioIntegration()
            integration.client = mock_client
            
            result = await integration.send_otp("+971501234567")
            
            assert result["status"] == "pending"
            assert result["to"] == "+971501234567"
    
    @pytest.mark.asyncio
    @patch('backend.integrations.twilio_integration.Client')
    async def test_send_otp_failure(self, mock_client_class):
        """Test OTP sending with error"""
        mock_client = Mock()
        mock_verify = Mock()
        mock_verify.services = Mock(side_effect=Exception("Twilio API Error"))
        mock_client.verify = mock_verify
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'ACtest',
            'TWILIO_AUTH_TOKEN': 'token',
            'TWILIO_VERIFY_SERVICE': 'VAtest'
        }):
            integration = TwilioIntegration()
            integration.client = mock_client
            
            result = await integration.send_otp("+971501234567")
            
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_verify_otp_without_client(self, integration_no_creds):
        """Test OTP verification when client is not configured"""
        result = await integration_no_creds.verify_otp("+971501234567", "123456")
        
        assert result["valid"] is True  # Test mode accepts 123456
        assert result.get("test_mode") is True
        
    @pytest.mark.asyncio
    async def test_verify_otp_test_mode_invalid_code(self, integration_no_creds):
        """Test OTP verification in test mode with wrong code"""
        result = await integration_no_creds.verify_otp("+971501234567", "999999")
        
        assert result["valid"] is False
        assert result.get("test_mode") is True
        
    @pytest.mark.asyncio
    @patch('backend.integrations.twilio_integration.Client')
    async def test_verify_otp_success(self, mock_client_class):
        """Test successful OTP verification"""
        mock_check = Mock()
        mock_check.status = "approved"
        
        mock_verify = Mock()
        mock_verify.verification_checks = Mock()
        mock_verify.verification_checks.create = Mock(return_value=mock_check)
        
        mock_verify_service = Mock()
        mock_verify_service.services = Mock(return_value=mock_verify)
        
        mock_client = Mock()
        mock_client.verify = mock_verify_service
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'ACtest',
            'TWILIO_AUTH_TOKEN': 'token',
            'TWILIO_VERIFY_SERVICE': 'VAtest'
        }):
            integration = TwilioIntegration()
            integration.client = mock_client
            
            result = await integration.verify_otp("+971501234567", "123456")
            
            assert result["valid"] is True
            assert result["status"] == "approved"
    
    @pytest.mark.asyncio
    @patch('backend.integrations.twilio_integration.Client')
    async def test_verify_otp_invalid_code(self, mock_client_class):
        """Test OTP verification with invalid code"""
        mock_check = Mock()
        mock_check.status = "pending"
        
        mock_verify = Mock()
        mock_verify.verification_checks = Mock()
        mock_verify.verification_checks.create = Mock(return_value=mock_check)
        
        mock_verify_service = Mock()
        mock_verify_service.services = Mock(return_value=mock_verify)
        
        mock_client = Mock()
        mock_client.verify = mock_verify_service
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'ACtest',
            'TWILIO_AUTH_TOKEN': 'token',
            'TWILIO_VERIFY_SERVICE': 'VAtest'
        }):
            integration = TwilioIntegration()
            integration.client = mock_client
            
            result = await integration.verify_otp("+971501234567", "000000")
            
            assert result["valid"] is False
            assert result["status"] == "pending"
    
    @pytest.mark.asyncio
    async def test_send_sms_without_client(self, integration_no_creds):
        """Test SMS sending when client is not configured"""
        result = await integration_no_creds.send_sms(
            to_number="+971501234567",
            message="Test message"
        )
        
        assert "error" in result
        assert result["test_mode"] is True
        
    @pytest.mark.asyncio
    @patch('backend.integrations.twilio_integration.Client')
    async def test_send_sms_success(self, mock_client_class):
        """Test successful SMS sending"""
        mock_message = Mock()
        mock_message.sid = "SMtest123"
        mock_message.status = "sent"
        
        mock_messages = Mock()
        mock_messages.create = Mock(return_value=mock_message)
        
        mock_client = Mock()
        mock_client.messages = mock_messages
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'ACtest',
            'TWILIO_AUTH_TOKEN': 'token',
            'TWILIO_PHONE_NUMBER': '+15551234567'
        }):
            integration = TwilioIntegration()
            integration.client = mock_client
            
            result = await integration.send_sms(
                to_number="+971501234567",
                message="Hello from Twilio!"
            )
            
            assert result["sid"] == "SMtest123"
            assert result["status"] == "sent"
    
    @pytest.mark.asyncio
    @patch('backend.integrations.twilio_integration.Client')
    async def test_send_sms_with_custom_from_number(self, mock_client_class):
        """Test SMS sending with custom from number"""
        mock_message = Mock()
        mock_message.sid = "SMtest456"
        mock_message.status = "queued"
        
        mock_messages = Mock()
        mock_messages.create = Mock(return_value=mock_message)
        
        mock_client = Mock()
        mock_client.messages = mock_messages
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'ACtest',
            'TWILIO_AUTH_TOKEN': 'token'
        }):
            integration = TwilioIntegration()
            integration.client = mock_client
            
            result = await integration.send_sms(
                to_number="+971501234567",
                message="Test message",
                from_number="+15559876543"
            )
            
            assert result["sid"] == "SMtest456"
            assert result["status"] == "queued"
    
    @pytest.mark.asyncio
    @patch('backend.integrations.twilio_integration.Client')
    async def test_send_sms_without_from_number_configured(self, mock_client_class):
        """Test SMS sending when no from number is configured"""
        mock_client = Mock()
        mock_client.messages = Mock()
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'ACtest',
            'TWILIO_AUTH_TOKEN': 'token'
        }, clear=True):
            integration = TwilioIntegration()
            integration.client = mock_client
            
            result = await integration.send_sms(
                to_number="+971501234567",
                message="Test"
            )
            
            assert "error" in result
            assert "No Twilio phone number configured" in result["error"]
    
    @pytest.mark.asyncio
    @patch('backend.integrations.twilio_integration.Client')
    async def test_send_sms_failure(self, mock_client_class):
        """Test SMS sending with error"""
        mock_messages = Mock()
        mock_messages.create = Mock(side_effect=Exception("Network error"))
        
        mock_client = Mock()
        mock_client.messages = mock_messages
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'ACtest',
            'TWILIO_AUTH_TOKEN': 'token',
            'TWILIO_PHONE_NUMBER': '+15551234567'
        }):
            integration = TwilioIntegration()
            integration.client = mock_client
            
            result = await integration.send_sms(
                to_number="+971501234567",
                message="Test"
            )
            
            assert "error" in result
            assert "Network error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_send_otp_international_number(self, integration):
        """Test OTP sending to various international numbers"""
        mock_verification = Mock()
        mock_verification.status = "pending"
        
        mock_verify = Mock()
        mock_verify.verifications = Mock()
        mock_verify.verifications.create = Mock(return_value=mock_verification)
        
        mock_verify_service = Mock()
        mock_verify_service.services = Mock(return_value=mock_verify)
        
        integration.client = Mock()
        integration.client.verify = mock_verify_service
        
        # Test various number formats
        numbers = ["+971501234567", "+1234567890", "+447123456789"]
        
        for number in numbers:
            result = await integration.send_otp(number)
            assert result["status"] == "pending"
            assert result["to"] == number
    
    def test_global_twilio_integration_instance(self):
        """Test global integration instance exists"""
        assert twilio_integration is not None
        assert isinstance(twilio_integration, TwilioIntegration)