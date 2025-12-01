"""Unit tests for azure_auth module."""

import os
import sys
from unittest import mock

import pytest

# Add the action src to path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "../../.github/actions/avm-action")
)

from src.azure_auth import (
    AuthMethod,
    AzureAuthenticator,
    AzureCredentials,
    create_authenticator_from_env,
)


class TestAzureCredentials:
    """Tests for AzureCredentials dataclass."""

    def test_creation_minimal(self):
        """Create credentials with minimal required fields."""
        creds = AzureCredentials(
            subscription_id="sub-123",
            tenant_id="tenant-456",
        )
        assert creds.subscription_id == "sub-123"
        assert creds.tenant_id == "tenant-456"
        assert creds.client_id == ""
        assert creds.client_secret == ""
        assert creds.token == ""
        assert creds.auth_method == AuthMethod.CLI

    def test_creation_full(self):
        """Create credentials with all fields."""
        creds = AzureCredentials(
            subscription_id="sub-123",
            tenant_id="tenant-456",
            client_id="client-789",
            client_secret="secret",
            token="token-abc",
            auth_method=AuthMethod.SERVICE_PRINCIPAL,
        )
        assert creds.client_id == "client-789"
        assert creds.client_secret == "secret"
        assert creds.token == "token-abc"
        assert creds.auth_method == AuthMethod.SERVICE_PRINCIPAL


class TestAzureAuthenticator:
    """Tests for AzureAuthenticator class."""

    @pytest.fixture
    def authenticator(self):
        """Create a basic authenticator for testing."""
        return AzureAuthenticator(
            subscription_id="sub-123",
            tenant_id="tenant-456",
            client_id="client-789",
        )

    def test_init(self, authenticator):
        """Authenticator should be initialized correctly."""
        assert authenticator.subscription_id == "sub-123"
        assert authenticator.tenant_id == "tenant-456"
        assert authenticator.client_id == "client-789"

    def test_detect_auth_method_oidc(self, authenticator):
        """Should detect OIDC when token request env var is set."""
        env = {"ACTIONS_ID_TOKEN_REQUEST_TOKEN": "token"}
        with mock.patch.dict(os.environ, env, clear=True):
            method = authenticator.detect_auth_method()
        assert method == AuthMethod.OIDC

    def test_detect_auth_method_service_principal_azure(self, authenticator):
        """Should detect service principal with AZURE_CLIENT_SECRET."""
        env = {"AZURE_CLIENT_SECRET": "secret"}
        with mock.patch.dict(os.environ, env, clear=True):
            method = authenticator.detect_auth_method()
        assert method == AuthMethod.SERVICE_PRINCIPAL

    def test_detect_auth_method_service_principal_arm(self, authenticator):
        """Should detect service principal with ARM_CLIENT_SECRET."""
        env = {"ARM_CLIENT_SECRET": "secret"}
        with mock.patch.dict(os.environ, env, clear=True):
            method = authenticator.detect_auth_method()
        assert method == AuthMethod.SERVICE_PRINCIPAL

    def test_detect_auth_method_managed_identity_msi(self, authenticator):
        """Should detect managed identity with MSI_ENDPOINT."""
        env = {"MSI_ENDPOINT": "http://localhost"}
        with mock.patch.dict(os.environ, env, clear=True):
            method = authenticator.detect_auth_method()
        assert method == AuthMethod.MANAGED_IDENTITY

    def test_detect_auth_method_managed_identity_identity(self, authenticator):
        """Should detect managed identity with IDENTITY_ENDPOINT."""
        env = {"IDENTITY_ENDPOINT": "http://localhost"}
        with mock.patch.dict(os.environ, env, clear=True):
            method = authenticator.detect_auth_method()
        assert method == AuthMethod.MANAGED_IDENTITY

    def test_detect_auth_method_defaults_to_cli(self, authenticator):
        """Should default to CLI when no specific env vars are set."""
        with mock.patch.dict(os.environ, {}, clear=True):
            method = authenticator.detect_auth_method()
        assert method == AuthMethod.CLI

    def test_authenticate_oidc_not_implemented(self, authenticator):
        """OIDC authentication should raise NotImplementedError."""
        with pytest.raises(NotImplementedError):
            authenticator.authenticate_oidc()

    def test_authenticate_service_principal_no_secret(self, authenticator):
        """Service principal auth without secret should raise ValueError."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                authenticator.authenticate_service_principal()
        assert "AZURE_CLIENT_SECRET" in str(exc_info.value)

    def test_authenticate_service_principal_with_secret(self, authenticator):
        """Service principal auth with secret should return credentials."""
        env = {"AZURE_CLIENT_SECRET": "my-secret"}
        with mock.patch.dict(os.environ, env, clear=True):
            creds = authenticator.authenticate_service_principal()

        assert creds.subscription_id == "sub-123"
        assert creds.tenant_id == "tenant-456"
        assert creds.client_id == "client-789"
        assert creds.client_secret == "my-secret"
        assert creds.auth_method == AuthMethod.SERVICE_PRINCIPAL

    def test_authenticate_cli(self, authenticator):
        """CLI authentication should return credentials."""
        creds = authenticator.authenticate_cli()

        assert creds.subscription_id == "sub-123"
        assert creds.tenant_id == "tenant-456"
        assert creds.client_id == "client-789"
        assert creds.auth_method == AuthMethod.CLI

    def test_set_terraform_env_vars_basic(self, authenticator):
        """Should generate basic Terraform env vars."""
        creds = AzureCredentials(
            subscription_id="sub-123",
            tenant_id="tenant-456",
        )
        env_vars = authenticator.set_terraform_env_vars(creds)

        assert env_vars["ARM_SUBSCRIPTION_ID"] == "sub-123"
        assert env_vars["ARM_TENANT_ID"] == "tenant-456"
        assert "ARM_CLIENT_SECRET" not in env_vars
        assert "ARM_OIDC_TOKEN" not in env_vars

    def test_set_terraform_env_vars_service_principal(self, authenticator):
        """Should include client secret for service principal."""
        creds = AzureCredentials(
            subscription_id="sub-123",
            tenant_id="tenant-456",
            client_id="client-789",
            client_secret="secret",
            auth_method=AuthMethod.SERVICE_PRINCIPAL,
        )
        env_vars = authenticator.set_terraform_env_vars(creds)

        assert env_vars["ARM_CLIENT_ID"] == "client-789"
        assert env_vars["ARM_CLIENT_SECRET"] == "secret"

    def test_set_terraform_env_vars_oidc(self, authenticator):
        """Should include OIDC token and flag."""
        creds = AzureCredentials(
            subscription_id="sub-123",
            tenant_id="tenant-456",
            client_id="client-789",
            token="oidc-token",
            auth_method=AuthMethod.OIDC,
        )
        env_vars = authenticator.set_terraform_env_vars(creds)

        assert env_vars["ARM_OIDC_TOKEN"] == "oidc-token"
        assert env_vars["ARM_USE_OIDC"] == "true"


class TestCreateAuthenticatorFromEnv:
    """Tests for create_authenticator_from_env function."""

    def test_returns_none_when_not_configured(self):
        """Should return None when subscription and tenant are not set."""
        with mock.patch.dict(os.environ, {}, clear=True):
            result = create_authenticator_from_env()
        assert result is None

    def test_returns_none_when_only_subscription_set(self):
        """Should return None when only subscription is set."""
        env = {"INPUT_AZURE_SUBSCRIPTION_ID": "sub-123"}
        with mock.patch.dict(os.environ, env, clear=True):
            result = create_authenticator_from_env()
        assert result is None

    def test_returns_authenticator_when_configured(self):
        """Should return authenticator when subscription and tenant are set."""
        env = {
            "INPUT_AZURE_SUBSCRIPTION_ID": "sub-123",
            "INPUT_AZURE_TENANT_ID": "tenant-456",
            "INPUT_AZURE_CLIENT_ID": "client-789",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            result = create_authenticator_from_env()

        assert result is not None
        assert result.subscription_id == "sub-123"
        assert result.tenant_id == "tenant-456"
        assert result.client_id == "client-789"
