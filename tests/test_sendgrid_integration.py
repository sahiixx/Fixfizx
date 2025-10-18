"""
Unit tests for backend/integrations/sendgrid_integration.py
Tests SendGrid email integration functionality
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import os
from backend.integrations.sendgrid_integration import SendGridIntegration, sendgrid_integration


class TestSendGridIntegration:
    """Test suite for SendGrid email integration"""
    
    @pytest.fixture
    def integration(self):
        """Create a SendGrid integration instance for testing"""
        with patch.dict(os.environ, {
            'SENDGRID_API_KEY': 'test_sendgrid_key_12345',
            'SENDGRID_FROM_EMAIL': 'test@example.com'
        }):
            return SendGridIntegration()
    
    @pytest.fixture
    def integration_no_key(self):
        """Create integration without API key"""
        with patch.dict(os.environ, {}, clear=True):
            return SendGridIntegration()
    
    def test_initialization_with_api_key(self, integration):
        """Test initialization with valid API key"""
        assert integration.api_key == 'test_sendgrid_key_12345'
        assert integration.from_email == 'test@example.com'
        assert integration.client is not None
        
    def test_initialization_without_api_key(self, integration_no_key):
        """Test initialization without API key"""
        assert integration_no_key.api_key is None
        assert integration_no_key.client is None
        
    def test_default_from_email(self):
        """Test default from email when not specified"""
        with patch.dict(os.environ, {'SENDGRID_API_KEY': 'test'}, clear=True):
            integration = SendGridIntegration()
            assert integration.from_email == "noreply@nowheredigital.ae"
    
    @pytest.mark.asyncio
    async def test_send_email_without_client(self, integration_no_key):
        """Test sending email when client is not configured"""
        result = await integration_no_key.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_content="<p>Test content</p>"
        )
        
        assert "error" in result
        assert result["error"] == "SendGrid not configured"
        assert result.get("test_mode") is True
        
    @pytest.mark.asyncio
    @patch('backend.integrations.sendgrid_integration.SendGridAPIClient')
    async def test_send_email_success(self, mock_client_class):
        """Test successful email sending"""
        mock_response = Mock()
        mock_response.status_code = 202
        
        mock_client = Mock()
        mock_client.send = Mock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {'SENDGRID_API_KEY': 'test_key'}):
            integration = SendGridIntegration()
            integration.client = mock_client
            
            result = await integration.send_email(
                to_email="recipient@example.com",
                subject="Test Subject",
                html_content="<p>Test HTML content</p>",
                plain_text="Test plain text"
            )
            
            assert result["status_code"] == 202
            assert result["success"] is True
            mock_client.send.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('backend.integrations.sendgrid_integration.SendGridAPIClient')
    async def test_send_email_failure(self, mock_client_class):
        """Test email sending with error"""
        mock_client = Mock()
        mock_client.send = Mock(side_effect=Exception("API Error"))
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {'SENDGRID_API_KEY': 'test_key'}):
            integration = SendGridIntegration()
            integration.client = mock_client
            
            result = await integration.send_email(
                to_email="recipient@example.com",
                subject="Test Subject",
                html_content="<p>Test content</p>"
            )
            
            assert "error" in result
            assert "API Error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_send_template_email_without_client(self, integration_no_key):
        """Test template email without configured client"""
        result = await integration_no_key.send_template_email(
            to_email="recipient@example.com",
            template_id="d-template123",
            dynamic_data={"name": "Test User"}
        )
        
        assert "error" in result
        assert result["test_mode"] is True
        
    @pytest.mark.asyncio
    @patch('backend.integrations.sendgrid_integration.SendGridAPIClient')
    async def test_send_template_email_success(self, mock_client_class):
        """Test successful template email sending"""
        mock_response = Mock()
        mock_response.status_code = 202
        
        mock_client = Mock()
        mock_client.send = Mock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {'SENDGRID_API_KEY': 'test_key'}):
            integration = SendGridIntegration()
            integration.client = mock_client
            
            result = await integration.send_template_email(
                to_email="recipient@example.com",
                template_id="d-template123",
                dynamic_data={"name": "John Doe", "order_id": "12345"}
            )
            
            assert result["status_code"] == 202
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_send_notification_welcome(self, integration):
        """Test sending welcome notification"""
        integration.client = Mock()
        mock_response = Mock()
        mock_response.status_code = 202
        integration.client.send = Mock(return_value=mock_response)
        
        result = await integration.send_notification(
            to_email="newuser@example.com",
            notification_type="welcome",
            data={"message": "Welcome to our platform!"}
        )
        
        assert result["status_code"] == 202
        assert result["success"] is True
        
    @pytest.mark.asyncio
    async def test_send_notification_alert(self, integration):
        """Test sending alert notification"""
        integration.client = Mock()
        mock_response = Mock()
        mock_response.status_code = 202
        integration.client.send = Mock(return_value=mock_response)
        
        result = await integration.send_notification(
            to_email="admin@example.com",
            notification_type="alert",
            data={
                "message": "Critical system alert",
                "details": "CPU usage exceeded 90%"
            }
        )
        
        assert result["status_code"] == 202
        assert result["success"] is True
        
    @pytest.mark.asyncio
    async def test_send_notification_report(self, integration):
        """Test sending report notification"""
        integration.client = Mock()
        mock_response = Mock()
        mock_response.status_code = 202
        integration.client.send = Mock(return_value=mock_response)
        
        result = await integration.send_notification(
            to_email="user@example.com",
            notification_type="report",
            data={"message": "Your monthly report is ready"}
        )
        
        assert result["status_code"] == 202
        assert result["success"] is True
        
    @pytest.mark.asyncio
    async def test_send_notification_unknown_type(self, integration):
        """Test sending notification with unknown type"""
        integration.client = Mock()
        mock_response = Mock()
        mock_response.status_code = 202
        integration.client.send = Mock(return_value=mock_response)
        
        result = await integration.send_notification(
            to_email="user@example.com",
            notification_type="unknown_type",
            data={"message": "Test message"}
        )
        
        # Should still work with default subject
        assert result["status_code"] == 202
        
    @pytest.mark.asyncio
    async def test_send_email_with_special_characters(self, integration):
        """Test sending email with special characters in content"""
        integration.client = Mock()
        mock_response = Mock()
        mock_response.status_code = 202
        integration.client.send = Mock(return_value=mock_response)
        
        result = await integration.send_email(
            to_email="user@example.com",
            subject="Test with émojis 🎉 and spëcial chàrs",
            html_content="<p>Content with <b>HTML</b> & special chars: €£¥</p>"
        )
        
        assert result["status_code"] == 202
        assert result["success"] is True
        
    @pytest.mark.asyncio
    async def test_send_email_multiple_recipients(self, integration):
        """Test sending email to multiple recipients"""
        integration.client = Mock()
        mock_response = Mock()
        mock_response.status_code = 202
        integration.client.send = Mock(return_value=mock_response)
        
        result = await integration.send_email(
            to_email=["user1@example.com", "user2@example.com"],
            subject="Bulk Email",
            html_content="<p>Test content</p>"
        )
        
        assert result["status_code"] == 202
        
    def test_global_sendgrid_integration_instance(self):
        """Test global integration instance exists"""
        assert sendgrid_integration is not None
        assert isinstance(sendgrid_integration, SendGridIntegration)