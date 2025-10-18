"""
Unit tests for backend/core/security_manager.py

Tests enterprise security features, RBAC, and compliance
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from backend.core.security_manager import (
    SecurityManager,
    UserRole,
    Permission,
    ComplianceStandard,
    AuditEvent,
    SecurityPolicy,
    security_manager
)


class TestUserRole:
    """Test user role enumeration"""

    def test_all_user_roles_defined(self):
        """Test that all user roles are properly defined"""
        assert UserRole.SUPER_ADMIN.value == "super_admin"
        assert UserRole.TENANT_ADMIN.value == "tenant_admin"
        assert UserRole.AGENT_MANAGER.value == "agent_manager"
        assert UserRole.ANALYST.value == "analyst"
        assert UserRole.OPERATOR.value == "operator"
        assert UserRole.VIEWER.value == "viewer"
        assert UserRole.API_USER.value == "api_user"


class TestPermission:
    """Test permission enumeration"""

    def test_agent_permissions_defined(self):
        """Test agent management permissions"""
        assert Permission.CREATE_AGENT.value == "create_agent"
        assert Permission.DELETE_AGENT.value == "delete_agent"
        assert Permission.CONFIGURE_AGENT.value == "configure_agent"

    def test_data_access_permissions_defined(self):
        """Test data access permissions"""
        assert Permission.VIEW_ANALYTICS.value == "view_analytics"
        assert Permission.EXPORT_DATA.value == "export_data"
        assert Permission.VIEW_INSIGHTS.value == "view_insights"

    def test_system_permissions_defined(self):
        """Test system management permissions"""
        assert Permission.MANAGE_USERS.value == "manage_users"
        assert Permission.CONFIGURE_SYSTEM.value == "configure_system"
        assert Permission.VIEW_AUDIT_LOGS.value == "view_audit_logs"


class TestComplianceStandard:
    """Test compliance standard enumeration"""

    def test_compliance_standards_defined(self):
        """Test that compliance standards are defined"""
        assert ComplianceStandard.SOC2_TYPE2.value == "soc2_type2"
        assert ComplianceStandard.ISO_27001.value == "iso_27001"
        assert ComplianceStandard.GDPR.value == "gdpr"
        assert ComplianceStandard.HIPAA.value == "hipaa"
        assert ComplianceStandard.PCI_DSS.value == "pci_dss"
        assert ComplianceStandard.UAE_DPA.value == "uae_dpa"


class TestSecurityManager:
    """Test suite for Security Manager"""

    @pytest.fixture
    def manager(self):
        """Create a security manager instance for testing"""
        return SecurityManager()

    def test_initialization(self, manager):
        """Test security manager initialization"""
        assert manager.config is not None
        assert manager.role_permissions is not None
        assert manager.security_policies == {}
        assert manager.active_sessions == {}
        assert manager.failed_attempts == {}

    def test_role_permissions_mapping(self, manager):
        """Test that role permissions are properly mapped"""
        assert UserRole.SUPER_ADMIN in manager.role_permissions
        assert UserRole.TENANT_ADMIN in manager.role_permissions
        assert UserRole.VIEWER in manager.role_permissions

        # Super admin should have all permissions
        super_admin_perms = manager.role_permissions[UserRole.SUPER_ADMIN]
        assert len(super_admin_perms) > 10

    def test_compliance_requirements_configured(self, manager):
        """Test that compliance requirements are configured"""
        assert ComplianceStandard.SOC2_TYPE2 in manager.compliance_requirements
        assert ComplianceStandard.GDPR in manager.compliance_requirements
        assert ComplianceStandard.UAE_DPA in manager.compliance_requirements

    def test_password_validation_min_length(self, manager):
        """Test password minimum length validation"""
        short_password = "Abc123!"  # noqa
        result = manager._validate_password_strength(short_password)
        assert result is False

    def test_password_validation_requires_uppercase(self, manager):
        """Test password requires uppercase letter"""
        no_upper = "abcdefgh1234!"
        result = manager._validate_password_strength(no_upper)
        assert result is False

    def test_password_validation_requires_lowercase(self, manager):
        """Test password requires lowercase letter"""
        no_lower = "ABCDEFGH1234!"
        result = manager._validate_password_strength(no_lower)
        assert result is False

    def test_password_validation_requires_digit(self, manager):
        """Test password requires digit"""
        no_digit = "Abcdefghijk!"
        result = manager._validate_password_strength(no_digit)
        assert result is False

    def test_password_validation_requires_special_char(self, manager):
        """Test password requires special character"""
        no_special = "Abcdefgh1234"
        result = manager._validate_password_strength(no_special)
        assert result is False

    def test_password_validation_strong_password(self, manager):
        """Test validation of strong password"""
        strong_password = "MySecureP@ssw0rd123"  # noqa
        result = manager._validate_password_strength(strong_password)
        assert result is True

    def test_hash_password_creates_hash(self, manager):
        """Test password hashing"""
        password = "TestPassword123!"  # noqa
        hashed = manager._hash_password(password)

        assert hashed is not None
        assert ":" in hashed  # Should contain salt:hash
        assert hashed != password

    def test_verify_password_correct(self, manager):
        """Test password verification with correct password"""
        password = "TestPassword123!"  # noqa
        hashed = manager._hash_password(password)

        result = manager._verify_password(password, hashed)
        assert result is True

    def test_verify_password_incorrect(self, manager):
        """Test password verification with incorrect password"""
        password = "TestPassword123!"  # noqa
        wrong_password = "WrongPassword456!"  # noqa
        hashed = manager._hash_password(password)

        result = manager._verify_password(wrong_password, hashed)
        assert result is False

    @pytest.mark.asyncio
    @patch('backend.core.security_manager.get_database')
    async def test_create_user_success(self, mock_get_db, manager):
        """Test successful user creation"""
        mock_db = AsyncMock()
        mock_db.users = AsyncMock()
        mock_db.users.insert_one = AsyncMock()
        mock_get_db.return_value = mock_db

        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "SecureP@ssw0rd123",
            "role": "viewer",
            "tenant_id": "tenant_123",
            "ip_address": "192.168.1.1",
            "user_agent": "Test Browser"
        }

        result = await manager.create_user(user_data)

        assert "user_id" in result
        assert result["email"] == "test@example.com"
        assert result["role"] == "viewer"
        assert "permissions" in result

    @pytest.mark.asyncio
    async def test_create_user_weak_password(self, manager):
        """Test user creation with weak password"""
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "weak",
            "role": "viewer"
        }

        result = await manager.create_user(user_data)

        assert "error" in result
        assert "security requirements" in result["error"]

    @pytest.mark.asyncio
    @patch('backend.core.security_manager.get_database')
    async def test_authenticate_user_success(self, mock_get_db, manager):
        """Test successful user authentication"""
        password = "SecureP@ssw0rd123"  # noqa
        password_hash = manager._hash_password(password)

        mock_db = AsyncMock()
        mock_db.users = AsyncMock()
        mock_db.users.find_one = AsyncMock(return_value={
            "user_id": "user_123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "viewer",
            "password_hash": password_hash,
            "active": True,
            "tenant_id": "tenant_123",
            "permissions": [Permission.VIEW_AGENT_STATUS.value]
        })
        mock_db.users.update_one = AsyncMock()
        mock_get_db.return_value = mock_db

        result = await manager.authenticate_user(
            email="test@example.com",
            password=password,
            ip_address="192.168.1.1",
            user_agent="Test Browser"
        )

        assert "token" in result
        assert "user" in result
        assert result["user"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    @patch('backend.core.security_manager.get_database')
    async def test_authenticate_user_invalid_credentials(self, mock_get_db, manager):
        """Test authentication with invalid credentials"""
        mock_db = AsyncMock()
        mock_db.users = AsyncMock()
        mock_db.users.find_one = AsyncMock(return_value=None)
        mock_get_db.return_value = mock_db

        result = await manager.authenticate_user(
            email="nonexistent@example.com",
            password="password",  # noqa
            ip_address="192.168.1.1",
            user_agent="Test Browser"
        )

        assert "error" in result
        assert "Invalid credentials" in result["error"]

    @pytest.mark.asyncio
    @patch('backend.core.security_manager.get_database')
    async def test_validate_permission_success(self, mock_get_db, manager):
        """Test successful permission validation"""
        mock_db = AsyncMock()
        mock_db.users = AsyncMock()
        mock_db.users.find_one = AsyncMock(return_value={
            "user_id": "user_123",
            "active": True,
            "tenant_id": "tenant_123",
            "permissions": [Permission.VIEW_ANALYTICS.value, Permission.EXPORT_DATA.value]
        })
        mock_get_db.return_value = mock_db

        result = await manager.validate_permission(
            user_id="user_123",
            permission=Permission.VIEW_ANALYTICS,
            resource="dashboard"
        )

        assert result is True

    @pytest.mark.asyncio
    @patch('backend.core.security_manager.get_database')
    async def test_validate_permission_denied(self, mock_get_db, manager):
        """Test permission validation denial"""
        mock_db = AsyncMock()
        mock_db.users = AsyncMock()
        mock_db.users.find_one = AsyncMock(return_value={
            "user_id": "user_123",
            "active": True,
            "permissions": [Permission.VIEW_ANALYTICS.value]
        })
        mock_get_db.return_value = mock_db

        result = await manager.validate_permission(
            user_id="user_123",
            permission=Permission.MANAGE_USERS
        )

        assert result is False

    @pytest.mark.asyncio
    @patch('backend.core.security_manager.get_database')
    async def test_create_security_policy_success(self, mock_get_db, manager):
        """Test creating security policy"""
        mock_db = AsyncMock()
        mock_db.security_policies = AsyncMock()
        mock_db.security_policies.insert_one = AsyncMock()
        mock_get_db.return_value = mock_db

        policy_data = {
            "name": "Password Policy",
            "description": "Password strength requirements",
            "rules": [{"min_length": 12}, {"require_special": True}],
            "compliance_standards": ["soc2_type2", "iso_27001"],
            "active": True
        }

        result = await manager.create_security_policy(policy_data)

        assert "policy_id" in result
        assert result["status"] == "created"

    @pytest.mark.asyncio
    @patch('backend.core.security_manager.get_database')
    async def test_generate_compliance_report(self, mock_get_db, manager):
        """Test generating compliance report"""
        mock_db = AsyncMock()
        mock_db.audit_logs = AsyncMock()
        mock_db.audit_logs.find = Mock(return_value=AsyncMock(
            to_list=AsyncMock(return_value=[
                {"risk_level": "low", "success": True},
                {"risk_level": "medium", "success": False}
            ])
        ))
        mock_get_db.return_value = mock_db

        with patch.object(manager.ai_service, 'generate_content', return_value="Compliance analysis"):
            result = await manager.generate_compliance_report(
                standard=ComplianceStandard.GDPR,
                tenant_id="tenant_123"
            )

        assert "standard" in result
        assert "metrics" in result
        assert "compliance_score" in result["metrics"]

    def test_rate_limiting_not_limited(self, manager):
        """Test rate limiting when under threshold"""
        result = manager._is_rate_limited("192.168.1.1", "login")
        assert result is False

    def test_rate_limiting_exceeded(self, manager):
        """Test rate limiting when threshold exceeded"""
        identifier = "192.168.1.100"
        action = "login"

        # Simulate multiple failed attempts
        for _ in range(6):
            manager.failed_attempts.setdefault(identifier, {}).setdefault(action, [])
            manager.failed_attempts[identifier][action].append(datetime.now(timezone.utc))

        result = manager._is_rate_limited(identifier, action)
        assert result is True

    def test_get_role_permissions_super_admin(self, manager):
        """Test getting permissions for super admin"""
        permissions = manager._get_role_permissions("super_admin")

        assert len(permissions) > 0
        # Super admin should have all permissions
        assert Permission.MANAGE_USERS in permissions
        assert Permission.CONFIGURE_SYSTEM in permissions

    def test_get_role_permissions_viewer(self, manager):
        """Test getting permissions for viewer"""
        permissions = manager._get_role_permissions("viewer")

        assert len(permissions) > 0
        # Viewer should have limited permissions
        assert Permission.VIEW_AGENT_STATUS in permissions
        # Should not have admin permissions
        assert Permission.MANAGE_USERS not in permissions

    def test_get_role_permissions_invalid_role(self, manager):
        """Test getting permissions for invalid role defaults to viewer"""
        permissions = manager._get_role_permissions("invalid_role")

        # Should default to viewer permissions
        assert len(permissions) > 0
        assert Permission.VIEW_AGENT_STATUS in permissions

    def test_global_security_manager_instance(self):
        """Test global security manager instance exists"""
        assert security_manager is not None
        assert isinstance(security_manager, SecurityManager)

    def test_jwt_configuration(self, manager):
        """Test JWT configuration"""
        assert "jwt_secret" in manager.config
        assert "jwt_expiry_hours" in manager.config
        assert manager.config["jwt_expiry_hours"] == 24

    def test_security_thresholds_configured(self, manager):
        """Test security thresholds are configured"""
        assert manager.config["max_login_attempts"] == 5
        assert manager.config["lockout_duration_minutes"] == 30
        assert manager.config["password_min_length"] == 12

    def test_api_rate_limits_configured(self, manager):
        """Test API rate limits are configured"""
        assert "api_rate_limits" in manager.config
        assert "default" in manager.config["api_rate_limits"]
        assert "premium" in manager.config["api_rate_limits"]
        assert "enterprise" in manager.config["api_rate_limits"]