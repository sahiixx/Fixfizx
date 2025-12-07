"""
Enhanced Configuration Management
Environment-specific settings with proper validation
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings with environment-based configuration"""
    
    # ================================
    # Environment Settings
    # ================================
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "NOWHERE.AI"
    VERSION: str = "1.0.0"
    
    # ================================
    # Server Settings
    # ================================
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    WORKERS: int = 4
    RELOAD: bool = True
    
    # ================================
    # Database Settings
    # ================================
    MONGO_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "nowhereai"
    DB_MAX_POOL_SIZE: int = 50
    DB_MIN_POOL_SIZE: int = 10
    DB_MAX_IDLE_TIME_MS: int = 45000
    DB_WAIT_QUEUE_TIMEOUT_MS: int = 5000
    
    # ================================
    # Security Settings
    # ================================
    JWT_SECRET: str = "default-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    
    # Password Requirements
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # ================================
    # CORS Settings
    # ================================
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # ================================
    # Rate Limiting
    # ================================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # ================================
    # API Keys (Optional)
    # ================================
    EMERGENT_LLM_KEY: Optional[str] = None
    
    # Payment
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Communication
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_VERIFY_SERVICE_SID: Optional[str] = None
    
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@nowheredigital.ae"
    
    # CRM Integrations
    HUBSPOT_API_KEY: Optional[str] = None
    SALESFORCE_CLIENT_ID: Optional[str] = None
    SALESFORCE_CLIENT_SECRET: Optional[str] = None
    
    # ================================
    # Caching Settings
    # ================================
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 300  # 5 minutes
    CACHE_MAX_SIZE: int = 1000
    
    # ================================
    # Logging Settings
    # ================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_SIZE_MB: int = 100
    LOG_BACKUP_COUNT: int = 10
    
    # ================================
    # Performance Settings
    # ================================
    REQUEST_TIMEOUT: int = 30
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ENABLE_GZIP: bool = True
    GZIP_MIN_SIZE: int = 1000
    
    # ================================
    # Feature Flags
    # ================================
    FEATURE_AI_ADVANCED: bool = True
    FEATURE_VOICE_AI: bool = True
    FEATURE_VISION_AI: bool = True
    FEATURE_WHITE_LABEL: bool = True
    FEATURE_MULTI_TENANCY: bool = True
    FEATURE_AGENT_SYSTEM: bool = True
    FEATURE_CRM_INTEGRATION: bool = False  # Requires API keys
    FEATURE_SMS_INTEGRATION: bool = False  # Requires API keys
    FEATURE_EMAIL_INTEGRATION: bool = False  # Requires API keys
    
    # ================================
    # Dubai/UAE Specific Settings
    # ================================
    DEFAULT_TIMEZONE: str = "Asia/Dubai"
    DEFAULT_CURRENCY: str = "AED"
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: List[str] = ["en", "ar"]
    
    # ================================
    # Monitoring & Analytics
    # ================================
    ENABLE_METRICS: bool = True
    METRICS_COLLECTION_INTERVAL: int = 60  # seconds
    ENABLE_ERROR_TRACKING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"
    
    # ================================
    # Property Methods
    # ================================
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing"""
        return self.ENVIRONMENT.lower() == "testing"
    
    @property
    def database_url(self) -> str:
        """Get full database URL"""
        return f"{self.MONGO_URL}/{self.DATABASE_NAME}"
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment"""
        if self.is_production:
            # In production, return only production domains
            return [origin for origin in self.CORS_ORIGINS if "localhost" not in origin]
        return self.CORS_ORIGINS
    
    def feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        feature_attr = f"FEATURE_{feature_name.upper()}"
        return getattr(self, feature_attr, False)
    
    def has_api_key(self, service: str) -> bool:
        """Check if API key is configured for a service"""
        key_map = {
            "stripe": self.STRIPE_SECRET_KEY,
            "twilio": self.TWILIO_ACCOUNT_SID,
            "sendgrid": self.SENDGRID_API_KEY,
            "hubspot": self.HUBSPOT_API_KEY,
            "emergent": self.EMERGENT_LLM_KEY,
        }
        return bool(key_map.get(service.lower()))
    
    def get_log_config(self) -> dict:
        """Get logging configuration"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default" if self.is_development else "json",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "json",
                    "filename": self.LOG_FILE,
                    "maxBytes": self.LOG_MAX_SIZE_MB * 1024 * 1024,
                    "backupCount": self.LOG_BACKUP_COUNT
                }
            },
            "root": {
                "level": self.LOG_LEVEL,
                "handlers": ["console", "file"] if self.is_production else ["console"]
            }
        }

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()

# Convenience functions
def is_production() -> bool:
    """Check if running in production"""
    return settings.is_production

def is_development() -> bool:
    """Check if running in development"""
    return settings.is_development

def feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return settings.feature_enabled(feature_name)

def has_api_key(service: str) -> bool:
    """Check if API key exists for service"""
    return settings.has_api_key(service)
