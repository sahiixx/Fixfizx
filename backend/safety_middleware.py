"""Safety Middleware — FastAPI middleware that scans all user input through SafetyCouncil.

Mount on the Fixfizx FastAPI app:
    from safety_middleware import SafetyMiddleware
    app.add_middleware(SafetyMiddleware)

This middleware intercepts all POST/PUT/PATCH requests and scans the request body
for dangerous patterns before they reach the application. Blocked requests receive
a 400 response with details about the safety violation.
"""
import json
import logging
import sys

sys.path.insert(0, "/mnt/c/Users/Sahil Khan/Downloads")

from sovereign_swarm import SafetyCouncil

logger = logging.getLogger("sahiixx.safety_middleware")

# Paths that should NOT be scanned (internal, health checks, etc.)
EXEMPT_PATHS = {
    "/api/health",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}

# Maximum request body size to scan (bytes)
MAX_BODY_SIZE = 100_000


class SafetyMiddleware:
    """ASGI middleware that scans request bodies for dangerous patterns.

    Blocks requests containing:
    - rm -rf / similar destructive commands
    - eval/exec with suspicious arguments
    - curl pipe to bash
    - SQL injection patterns (in safety mode)
    - Shell injection patterns

    Logs all violations to the audit trail.
    """

    def __init__(self, app, council: SafetyCouncil = None):
        self.app = app
        self.council = council or SafetyCouncil()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        method = scope.get("method", "")

        # Only scan write operations on API endpoints
        if method not in ("POST", "PUT", "PATCH") or path in EXEMPT_PATHS:
            await self.app(scope, receive, send)
            return

        # Read the request body
        body = b""
        body_received = False

        async def receive_with_body():
            nonlocal body, body_received
            if not body_received:
                message = await receive()
                body = message.get("body", b"")
                # Handle larger bodies across multiple messages
                while message.get("more_body", False):
                    message = await receive()
                    body += message.get("body", b"")
                body_received = True
                return message
            return {"type": "http.disconnect"}

        message = await receive_with_body()

        # Skip if body is too large
        if len(body) > MAX_BODY_SIZE:
            await self.app(scope, receive, send)
            return

        # Extract text content for scanning
        try:
            text_content = body.decode("utf-8", errors="replace")
            # Also try to extract string values from JSON
            try:
                json_body = json.loads(text_content)
                text_parts = []
                for value in json_body.values() if isinstance(json_body, dict) else []:
                    if isinstance(value, str):
                        text_parts.append(value)
                    elif isinstance(value, dict):
                        text_parts.append(json.dumps(value))
                    elif isinstance(value, list):
                        text_parts.extend(str(v) for v in value)
                text_content = " ".join(text_parts) if text_parts else text_content
            except (json.JSONDecodeError, AttributeError):
                pass  # Not JSON, scan raw text

            # Run safety scan
            result = self.council.scan(text_content)

            if result["blocked"]:
                logger.warning("SafetyMiddleware blocked request to %s: %s", path, result["rule"])
                # Send 400 response
                response_body = json.dumps({
                    "error": "blocked_by_safety",
                    "rule": result["rule"],
                    "confidence": result.get("confidence", 0),
                    "message": "Request blocked by safety middleware. Remove dangerous patterns and try again.",
                }).encode("utf-8")

                await send({
                    "type": "http.response.start",
                    "status": 400,
                    "headers": [
                        [b"content-type", b"application/json"],
                        [b"content-length", str(len(response_body)).encode()],
                    ],
                })
                await send({
                    "type": "http.response.body",
                    "body": response_body,
                })
                return

        except Exception as e:
            logger.error("SafetyMiddleware scan error: %s", e)
            # Don't block on scan errors

        # Pass through to the app
        await self.app(scope, receive, send)