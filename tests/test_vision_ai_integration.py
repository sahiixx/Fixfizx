"""
Unit tests for backend/integrations/vision_ai_integration.py
Tests Vision AI image analysis integration
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import os
from datetime import datetime, timezone
from backend.integrations.vision_ai_integration import VisionAIIntegration, vision_ai_integration


class TestVisionAIIntegration:
    """Test suite for Vision AI integration"""
    
    @pytest.fixture
    def integration(self):
        """Create a Vision AI integration instance for testing"""
        with patch.dict(os.environ, {'EMERGENT_LLM_KEY': 'sk-test-key-12345'}):
            return VisionAIIntegration()
    
    def test_initialization(self, integration):
        """Test initialization with API key"""
        assert integration.api_key == 'sk-test-key-12345'
        
    def test_default_api_key(self):
        """Test default API key when not provided"""
        with patch.dict(os.environ, {}, clear=True):
            integration = VisionAIIntegration()
            assert integration.api_key == 'sk-test-default-api-key'
    
    @pytest.mark.asyncio
    @patch('backend.integrations.vision_ai_integration.LlmChat')
    async def test_analyze_image_base64_success(self, mock_llm_chat_class):
        """Test successful image analysis with base64 data"""
        # Mock the chat response
        mock_chat_instance = Mock()
        mock_chat_instance.with_model = Mock(return_value=mock_chat_instance)
        mock_chat_instance.send_message = AsyncMock(
            return_value="This image shows a beautiful sunset over the ocean."
        )
        mock_llm_chat_class.return_value = mock_chat_instance
        
        integration = VisionAIIntegration()
        
        result = await integration.analyze_image(
            image_data="base64_encoded_image_data",
            prompt="Describe this image",
            image_type="base64"
        )
        
        assert "analysis" in result
        assert "model" in result
        assert result["model"] == "gpt-4o"
        assert "timestamp" in result
        
    @pytest.mark.asyncio
    @patch('backend.integrations.vision_ai_integration.LlmChat')
    async def test_analyze_image_with_custom_prompt(self, mock_llm_chat_class):
        """Test image analysis with custom prompt"""
        mock_chat_instance = Mock()
        mock_chat_instance.with_model = Mock(return_value=mock_chat_instance)
        mock_chat_instance.send_message = AsyncMock(
            return_value="The image contains three people in business attire."
        )
        mock_llm_chat_class.return_value = mock_chat_instance
        
        integration = VisionAIIntegration()
        
        custom_prompt = "How many people are in this image and what are they wearing?"
        result = await integration.analyze_image(
            image_data="base64_data",
            prompt=custom_prompt,
            image_type="base64"
        )
        
        assert "analysis" in result
        assert result["analysis"] == "The image contains three people in business attire."
    
    @pytest.mark.asyncio
    async def test_analyze_image_error_handling(self):
        """Test error handling in image analysis"""
        integration = VisionAIIntegration()
        
        with patch('backend.integrations.vision_ai_integration.LlmChat', 
                   side_effect=Exception("API connection failed")):
            result = await integration.analyze_image(
                image_data="invalid_data",
                prompt="Analyze this"
            )
            
            assert "error" in result
            assert "API connection failed" in result["error"]
    
    @pytest.mark.asyncio
    @patch('backend.integrations.vision_ai_integration.LlmChat')
    async def test_analyze_image_creates_unique_session(self, mock_llm_chat_class):
        """Test that each analysis creates a unique session ID"""
        mock_chat_instance = Mock()
        mock_chat_instance.with_model = Mock(return_value=mock_chat_instance)
        mock_chat_instance.send_message = AsyncMock(return_value="Analysis result")
        
        session_ids = []
        
        def capture_session_id(*_args, **kwargs):
            session_ids.append(kwargs.get('session_id'))
            return mock_chat_instance
        
        mock_llm_chat_class.side_effect = capture_session_id
        
        integration = VisionAIIntegration()
        
        # Perform multiple analyses
        await integration.analyze_image("data1", "prompt1")
        await integration.analyze_image("data2", "prompt2")
        
        # Check that session IDs are unique
        assert len(session_ids) == 2
        assert session_ids[0] != session_ids[1]
        assert all(sid.startswith("vision_") for sid in session_ids if sid)
    
    @pytest.mark.asyncio
    @patch('backend.integrations.vision_ai_integration.LlmChat')
    async def test_analyze_image_uses_gpt4o_model(self, mock_llm_chat_class):
        """Test that the integration uses GPT-4o model"""
        mock_chat_instance = Mock()
        mock_chat_instance.with_model = Mock(return_value=mock_chat_instance)
        mock_chat_instance.send_message = AsyncMock(return_value="Result")
        mock_llm_chat_class.return_value = mock_chat_instance
        
        integration = VisionAIIntegration()
        
        await integration.analyze_image("data", "prompt")
        
        mock_chat_instance.with_model.assert_called_once_with("openai", "gpt-4o")
    
    @pytest.mark.asyncio
    async def test_analyze_image_url_not_implemented(self):
        """Test that URL analysis returns not implemented message"""
        integration = VisionAIIntegration()
        
        result = await integration.analyze_image_url(
            image_url="https://example.com/image.jpg",
            prompt="Analyze this"
        )
        
        assert "error" in result
        assert "not yet implemented" in result["error"]
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_analyze_image_url_error_handling(self):
        """Test error handling for URL analysis"""
        integration = VisionAIIntegration()
        
        with patch('backend.integrations.vision_ai_integration.logger'):
            result = await integration.analyze_image_url(
                image_url="invalid://url",
                prompt="Test"
            )
            
            assert "error" in result
    
    def test_get_supported_formats(self):
        """Test getting supported image formats"""
        integration = VisionAIIntegration()
        
        formats = integration.get_supported_formats()
        
        assert "formats" in formats
        assert "max_size_mb" in formats
        assert "input_types" in formats
        
        assert "jpeg" in formats["formats"]
        assert "png" in formats["formats"]
        assert "webp" in formats["formats"]
        
        assert formats["max_size_mb"] == 20
        
        assert "base64" in formats["input_types"]
        assert "file_path" in formats["input_types"]
        assert "url" in formats["input_types"]
    
    def test_supported_formats_includes_common_types(self):
        """Test that supported formats include common image types"""
        integration = VisionAIIntegration()
        
        formats = integration.get_supported_formats()
        supported = formats["formats"]
        
        common_formats = ["jpeg", "jpg", "png", "gif"]
        for fmt in common_formats:
            assert fmt in supported, f"{fmt} should be in supported formats"
    
    def test_max_file_size_is_reasonable(self):
        """Test that max file size is reasonable"""
        integration = VisionAIIntegration()
        
        formats = integration.get_supported_formats()
        max_size = formats["max_size_mb"]
        
        assert max_size > 0
        assert max_size <= 100  # Should not be more than 100MB
    
    @pytest.mark.asyncio
    @patch('backend.integrations.vision_ai_integration.LlmChat')
    async def test_analyze_image_with_default_prompt(self, mock_llm_chat_class):
        """Test image analysis with default prompt"""
        mock_chat_instance = Mock()
        mock_chat_instance.with_model = Mock(return_value=mock_chat_instance)
        mock_chat_instance.send_message = AsyncMock(return_value="Detailed analysis")
        mock_llm_chat_class.return_value = mock_chat_instance
        
        integration = VisionAIIntegration()
        
        result = await integration.analyze_image("image_data")
        
        assert "analysis" in result
        # Default prompt should be used
        assert result["analysis"] == "Detailed analysis"
    
    @pytest.mark.asyncio
    @patch('backend.integrations.vision_ai_integration.LlmChat')
    async def test_analyze_image_includes_timestamp(self, mock_llm_chat_class):
        """Test that analysis result includes timestamp"""
        mock_chat_instance = Mock()
        mock_chat_instance.with_model = Mock(return_value=mock_chat_instance)
        mock_chat_instance.send_message = AsyncMock(return_value="Analysis")
        mock_llm_chat_class.return_value = mock_chat_instance
        
        integration = VisionAIIntegration()
        
        result = await integration.analyze_image("data", "prompt")
        
        assert "timestamp" in result
        # Verify it's a valid ISO format timestamp
        try:
            datetime.fromisoformat(result["timestamp"])
        except ValueError:
            pytest.fail("Timestamp is not in valid ISO format")
    
    @pytest.mark.asyncio
    @patch('backend.integrations.vision_ai_integration.LlmChat')
    async def test_analyze_multiple_images_sequentially(self, mock_llm_chat_class):
        """Test analyzing multiple images in sequence"""
        mock_chat_instance = Mock()
        mock_chat_instance.with_model = Mock(return_value=mock_chat_instance)
        
        responses = ["First image analysis", "Second image analysis", "Third image analysis"]
        mock_chat_instance.send_message = AsyncMock(side_effect=responses)
        mock_llm_chat_class.return_value = mock_chat_instance
        
        integration = VisionAIIntegration()
        
        results = []
        for i in range(3):
            result = await integration.analyze_image(f"image_data_{i}", f"Prompt {i}")
            results.append(result)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert "analysis" in result
            assert result["analysis"] == responses[i]
    
    def test_global_vision_ai_integration_instance(self):
        """Test global integration instance exists"""
        assert vision_ai_integration is not None
        assert isinstance(vision_ai_integration, VisionAIIntegration)