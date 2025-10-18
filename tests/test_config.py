"""
Unit tests for backend/config.py
Tests configuration management and environment variable handling
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from backend.config import Settings, settings


class TestSettings:
    """Test suite for Settings configuration class"""
    
    def test_default_settings(self):
        """Test that default settings are properly initialized"""
        test_settings = Settings()
        
        assert test_settings.mongo_url == "mongodb://localhost:27017"
        assert test_settings.db_name == "nowhere_digital"
        assert test_settings.jwt_algorithm == "HS256"
        assert test_settings.jwt_expiration == 24 * 60 * 60
        assert test_settings.debug is False
        
    def test_cors_origins_list(self):
        """Test CORS origins are properly defined"""
        test_settings = Settings()
        
        assert isinstance(test_settings.cors_origins, list)
        assert len(test_settings.cors_origins) > 0
        assert "http://localhost:3000" in test_settings.cors_origins
        
    def test_allowed_file_types(self):
        """Test allowed file types configuration"""
        test_settings = Settings()
        
        assert isinstance(test_settings.allowed_file_types, list)
        assert "image/jpeg" in test_settings.allowed_file_types
        assert "image/png" in test_settings.allowed_file_types
        assert "application/pdf" in test_settings.allowed_file_types
        
    def test_max_file_size(self):
        """Test max file size is within reasonable bounds"""
        test_settings = Settings()
        
        assert test_settings.max_file_size == 10 * 1024 * 1024  # 10MB
        assert test_settings.max_file_size > 0
        
    def test_rate_limiting_config(self):
        """Test rate limiting configuration"""
        test_settings = Settings()
        
        assert test_settings.rate_limit_requests == 100
        assert test_settings.rate_limit_period == 60
        assert test_settings.rate_limit_period > 0
        
    @patch.dict(os.environ, {
        'MONGO_URL': 'mongodb://testhost:27017',
        'DB_NAME': 'test_db',
        'DEBUG': 'true',
        'JWT_SECRET': 'test-secret-key'
    })
    def test_environment_variable_override(self):
        """Test that environment variables override default settings"""
        test_settings = Settings()
        
        assert test_settings.mongo_url == 'mongodb://testhost:27017'
        assert test_settings.db_name == 'test_db'
        assert test_settings.debug is True
        assert test_settings.jwt_secret == 'test-secret-key'  # noqa: S105
        
    @patch.dict(os.environ, {
        'SENDGRID_API_KEY': 'sg-test-key',
        'SENDGRID_FROM_EMAIL': 'test@example.com',
        'ADMIN_EMAIL': 'admin@test.com'
    })
    def test_email_configuration(self):
        """Test email configuration from environment"""
        test_settings = Settings()
        
        assert test_settings.sendgrid_api_key == 'sg-test-key'
        assert test_settings.sendgrid_from_email == 'test@example.com'
        assert test_settings.admin_email == 'admin@test.com'
        
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-openai',
        'EMERGENT_LLM_KEY': 'sk-test-emergent',
        'DEFAULT_AI_MODEL': 'gpt-4'
    })
    def test_ai_configuration(self):
        """Test AI service configuration"""
        test_settings = Settings()
        
        assert test_settings.openai_api_key == 'sk-test-openai'
        assert test_settings.emergent_llm_key == 'sk-test-emergent'
        assert test_settings.default_ai_model == 'gpt-4'
        assert test_settings.ai_provider == 'openai'
        
    @patch.dict(os.environ, {
        'STRIPE_API_KEY': 'sk_test_stripe',
        'TWILIO_ACCOUNT_SID': 'ACtest123',
        'TWILIO_AUTH_TOKEN': 'test_token',
        'TWILIO_VERIFY_SERVICE': 'VAtest123'
    })
    def test_integration_credentials(self):
        """Test third-party integration credentials"""
        test_settings = Settings()
        
        assert test_settings.stripe_api_key == 'sk_test_stripe'
        assert test_settings.twilio_account_sid == 'ACtest123'
        assert test_settings.twilio_auth_token == 'test_token'  # noqa: S105
        assert test_settings.twilio_verify_service == 'VAtest123'
        
    def test_api_prefix(self):
        """Test API prefix configuration"""
        test_settings = Settings()
        
        assert test_settings.api_prefix == "/api"
        assert test_settings.api_prefix.startswith("/")
        
    def test_email_templates_directory(self):
        """Test email templates directory configuration"""
        test_settings = Settings()
        
        assert test_settings.email_templates_dir == "email_templates"
        assert isinstance(test_settings.email_templates_dir, str)
        
    def test_global_settings_instance(self):
        """Test global settings instance is accessible"""
        assert settings is not None
        assert isinstance(settings, Settings)


class TestSettingsValidation:
    """Test configuration validation and edge cases"""
    
    @patch.dict(os.environ, {'DEBUG': 'false'})
    def test_debug_false_string(self):
        """Test debug mode with 'false' string"""
        test_settings = Settings()
        assert test_settings.debug is False
        
    @patch.dict(os.environ, {'DEBUG': 'True'})
    def test_debug_true_capitalized(self):
        """Test debug mode with capitalized 'True'"""
        test_settings = Settings()
        assert test_settings.debug is True
        
    @patch.dict(os.environ, {'DEBUG': '1'})
    def test_debug_with_numeric_value(self):
        """Test debug mode with numeric value"""
        test_settings = Settings()
        # Should be false since it's not "true"
        assert test_settings.debug is False
        
    def test_jwt_expiration_is_positive(self):
        """Test JWT expiration is a positive number"""
        test_settings = Settings()
        assert test_settings.jwt_expiration > 0
        
    def test_rate_limits_are_reasonable(self):
        """Test rate limit values are within reasonable bounds"""
        test_settings = Settings()
        
        assert 0 < test_settings.rate_limit_requests <= 10000
        assert 0 < test_settings.rate_limit_period <= 3600