"""
Security Headers Middleware
Adds essential security headers to all responses
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    Protects against common web vulnerabilities
    """
    
    def __init__(self, app, config: dict = None):
        super().__init__(app)
        self.config = config or {}
        logger.info("✅ Security headers middleware initialized")
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response"""
        response = await call_next(request)
        
        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = self.config.get(
            "x_frame_options", "SAMEORIGIN"
        )
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Strict Transport Security (HTTPS only)
        if self.config.get("enable_hsts", True):
            response.headers["Strict-Transport-Security"] = self.config.get(
                "hsts_header",
                "max-age=31536000; includeSubDomains"
            )
        
        # Content Security Policy
        if self.config.get("enable_csp", True):
            response.headers["Content-Security-Policy"] = self.config.get(
                "csp_header",
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'"
            )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = self.config.get(
            "referrer_policy",
            "strict-origin-when-cross-origin"
        )
        
        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = self.config.get(
            "permissions_policy",
            "geolocation=(), microphone=(), camera=()"
        )
        
        # Remove server header
        if "Server" in response.headers:
            del response.headers["Server"]
        
        # Remove X-Powered-By header
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]
        
        return response

def get_security_headers_config(environment: str = "production") -> dict:
    """
    Get security headers configuration based on environment
    
    Args:
        environment: Environment (development, production)
    
    Returns:
        Configuration dictionary
    """
    if environment == "production":
        return {
            "enable_hsts": True,
            "hsts_header": "max-age=31536000; includeSubDomains; preload",
            "enable_csp": True,
            "csp_header": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https://fonts.gstatic.com; "
                "connect-src 'self' https://api.openai.com https://api.anthropic.com; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            "x_frame_options": "DENY",
            "referrer_policy": "strict-origin-when-cross-origin",
            "permissions_policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=()"
            )
        }
    else:
        # Development - More relaxed for debugging
        return {
            "enable_hsts": False,
            "enable_csp": False,
            "x_frame_options": "SAMEORIGIN",
            "referrer_policy": "no-referrer-when-downgrade",
            "permissions_policy": "geolocation=(), microphone=(), camera=()"
        }
