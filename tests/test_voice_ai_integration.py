"""
Unit tests for backend/integrations/voice_ai_integration.py
Tests Voice AI speech integration
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import os
from backend.integrations.voice_ai_integration import VoiceAIIntegration, voice_ai_integration


class TestVoiceAIIntegration:
    """Test suite for Voice AI integration"""
    
    @pytest.fixture
    def integration(self):
        """Create a Voice AI integration instance for testing"""
        with patch.dict(os.environ, {'EMERGENT_LLM_KEY': 'sk-test-voice-key'}):
            return VoiceAIIntegration()
    
    def test_initialization(self, integration):
        """Test initialization with API key"""
        assert integration.api_key == 'sk-test-voice-key'
        assert integration.realtime_chat is None
        
    def test_default_api_key(self):
        """Test default API key when not provided"""
        with patch.dict(os.environ, {}, clear=True):
            integration = VoiceAIIntegration()
            assert integration.api_key == 'sk-test-default-key'
    
    @patch('backend.integrations.voice_ai_integration.OpenAIChatRealtime')
    def test_get_realtime_client_creates_instance(self, mock_realtime_class):
        """Test that get_realtime_client creates client instance"""
        mock_client = Mock()
        mock_realtime_class.return_value = mock_client
        
        integration = VoiceAIIntegration()
        
        client = integration.get_realtime_client()
        
        assert client is not None
        assert integration.realtime_chat is not None
        mock_realtime_class.assert_called_once_with(api_key=integration.api_key)
    
    @patch('backend.integrations.voice_ai_integration.OpenAIChatRealtime')
    def test_get_realtime_client_reuses_instance(self, mock_realtime_class):
        """Test that get_realtime_client reuses existing instance"""
        mock_client = Mock()
        mock_realtime_class.return_value = mock_client
        
        integration = VoiceAIIntegration()
        
        client1 = integration.get_realtime_client()
        client2 = integration.get_realtime_client()
        
        # Should only create once
        assert mock_realtime_class.call_count == 1
        assert client1 is client2
    
    @pytest.mark.asyncio
    @patch('backend.integrations.voice_ai_integration.OpenAIChatRealtime')
    async def test_create_voice_session_success(self, mock_realtime_class):
        """Test successful voice session creation"""
        mock_client = Mock()
        mock_realtime_class.return_value = mock_client
        
        integration = VoiceAIIntegration()
        
        result = await integration.create_voice_session()
        
        assert result["status"] == "ready"
        assert result["client_ready"] is True
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_create_voice_session_error_handling(self):
        """Test error handling in voice session creation"""
        integration = VoiceAIIntegration()
        
        with patch.object(integration, 'get_realtime_client', 
                         side_effect=Exception("Connection failed")):
            result = await integration.create_voice_session()
            
            assert "error" in result
            assert "Connection failed" in result["error"]
    
    def test_get_integration_info(self):
        """Test getting integration information"""
        integration = VoiceAIIntegration()
        
        info = integration.get_integration_info()
        
        assert "provider" in info
        assert info["provider"] == "OpenAI Realtime"
        assert "capabilities" in info
        assert "status" in info
    
    def test_get_integration_info_capabilities(self):
        """Test that integration info includes all capabilities"""
        integration = VoiceAIIntegration()
        
        info = integration.get_integration_info()
        capabilities = info["capabilities"]
        
        expected_capabilities = [
            "Real-time voice chat",
            "Speech-to-text",
            "Text-to-speech",
            "WebRTC support"
        ]
        
        for capability in expected_capabilities:
            assert capability in capabilities
    
    def test_get_integration_info_status_with_key(self):
        """Test integration status when API key is configured"""
        with patch.dict(os.environ, {'EMERGENT_LLM_KEY': 'sk-valid-key'}):
            integration = VoiceAIIntegration()
            
            info = integration.get_integration_info()
            
            assert info["status"] == "available"
    
    def test_get_integration_info_status_without_key(self):
        """Test integration status when API key is not configured"""
        integration = VoiceAIIntegration()
        integration.api_key = None
        
        info = integration.get_integration_info()
        
        assert info["status"] == "not_configured"
    
    @pytest.mark.asyncio
    @patch('backend.integrations.voice_ai_integration.OpenAIChatRealtime')
    async def test_create_multiple_voice_sessions(self, mock_realtime_class):
        """Test creating multiple voice sessions"""
        mock_client = Mock()
        mock_realtime_class.return_value = mock_client
        
        integration = VoiceAIIntegration()
        
        results = []
        for _ in range(3):
            result = await integration.create_voice_session()
            results.append(result)
        
        assert len(results) == 3
        for result in results:
            assert result["status"] == "ready"
            assert result["client_ready"] is True
    
    @patch('backend.integrations.voice_ai_integration.OpenAIChatRealtime')
    def test_realtime_client_uses_correct_api_key(self, mock_realtime_class):
        """Test that realtime client is created with correct API key"""
        test_api_key = "sk-test-specific-key"
        
        with patch.dict(os.environ, {'EMERGENT_LLM_KEY': test_api_key}):
            integration = VoiceAIIntegration()
            
            integration.get_realtime_client()
            
            mock_realtime_class.assert_called_once_with(api_key=test_api_key)
    
    def test_integration_info_provider_name(self):
        """Test that provider name is correctly identified"""
        integration = VoiceAIIntegration()
        
        info = integration.get_integration_info()
        
        assert info["provider"] == "OpenAI Realtime"
        assert isinstance(info["provider"], str)
    
    def test_integration_info_returns_dict(self):
        """Test that integration info returns a dictionary"""
        integration = VoiceAIIntegration()
        
        info = integration.get_integration_info()
        
        assert isinstance(info, dict)
        assert len(info) >= 3  # Should have provider, capabilities, status
    
    @pytest.mark.asyncio
    async def test_create_voice_session_returns_dict(self):
        """Test that create_voice_session returns a dictionary"""
        with patch('backend.integrations.voice_ai_integration.OpenAIChatRealtime'):
            integration = VoiceAIIntegration()
            
            result = await integration.create_voice_session()
            
            assert isinstance(result, dict)
    
    def test_global_voice_ai_integration_instance(self):
        """Test global integration instance exists"""
        assert voice_ai_integration is not None
        assert isinstance(voice_ai_integration, VoiceAIIntegration)