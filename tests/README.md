# Unit Tests for NOWHERE Digital Platform

This directory contains comprehensive unit tests for the backend integration and core modules.

## Test Coverage

### Configuration Tests
- `test_config.py`: Tests for configuration management and environment variables

### Integration Tests
- `test_sendgrid_integration.py`: SendGrid email integration tests
- `test_twilio_integration.py`: Twilio SMS and OTP verification tests
- `test_stripe_integration.py`: Stripe payment integration tests
- `test_vision_ai_integration.py`: OpenAI Vision AI image analysis tests
- `test_voice_ai_integration.py`: OpenAI Voice AI speech integration tests
- `test_crm_integrations.py`: Multi-provider CRM integration tests (HubSpot, Salesforce, etc.)

### Core Module Tests
- `test_security_manager.py`: Enterprise security, RBAC, and compliance tests
- `test_performance_optimizer.py`: Performance optimization, caching, and monitoring tests

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_config.py

# Run with coverage
pytest --cov=backend tests/

# Run with verbose output
pytest -v tests/

# Run specific test class
pytest tests/test_config.py::TestSettings

# Run specific test method
pytest tests/test_config.py::TestSettings::test_default_settings
```

## Test Structure

Tests follow a consistent structure:
- Fixtures for creating test instances
- Happy path tests
- Edge case tests
- Error handling tests
- Validation tests
- Integration tests with mocked dependencies

## Mocking Strategy

- External API calls are mocked using `unittest.mock`
- Database operations use AsyncMock
- Environment variables use `patch.dict(os.environ, ...)`
- Time-sensitive operations use fixed timestamps

## Coverage Goals

- Aim for >80% code coverage
- Focus on critical paths and business logic
- Test all public interfaces
- Validate error handling