"""Azure authentication helpers for AVM Action.

This module provides abstractions for Azure authentication,
including support for GitHub OIDC and Service Principal authentication.

TODO: Implement full production auth flows in future PRs.
See docs/architecture.md for extension plans.
"""

import os
from dataclasses import dataclass
from enum import Enum


class AuthMethod(Enum):
    """Supported Azure authentication methods."""

    OIDC = "oidc"
    SERVICE_PRINCIPAL = "service_principal"
    MANAGED_IDENTITY = "managed_identity"
    CLI = "cli"


@dataclass
class AzureCredentials:
    """Azure credentials container.

    Attributes:
        subscription_id: Azure Subscription ID.
        tenant_id: Azure Tenant ID.
        client_id: Azure Client ID.
        client_secret: Azure Client Secret (for service principal auth).
        token: Access token (for OIDC auth).
        auth_method: The authentication method used.
    """

    subscription_id: str
    tenant_id: str
    client_id: str = ""
    client_secret: str = ""
    token: str = ""
    auth_method: AuthMethod = AuthMethod.CLI


class AzureAuthenticator:
    """Handles Azure authentication for Terraform operations.

    This class provides a thin abstraction for Azure authentication,
    supporting multiple authentication methods.

    TODO: Implement full OIDC and service principal flows.
    """

    def __init__(
        self,
        subscription_id: str,
        tenant_id: str,
        client_id: str | None = None,
    ):
        """Initialize the Azure authenticator.

        Args:
            subscription_id: Azure Subscription ID.
            tenant_id: Azure Tenant ID.
            client_id: Optional Azure Client ID.
        """
        self.subscription_id = subscription_id
        self.tenant_id = tenant_id
        self.client_id = client_id or ""

    def detect_auth_method(self) -> AuthMethod:
        """Detect the appropriate authentication method.

        This examines the environment to determine which auth method to use.

        Returns:
            The detected AuthMethod.
        """
        # Check for GitHub OIDC token
        if os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN"):
            return AuthMethod.OIDC

        # Check for service principal credentials
        if os.environ.get("AZURE_CLIENT_SECRET") or os.environ.get("ARM_CLIENT_SECRET"):
            return AuthMethod.SERVICE_PRINCIPAL

        # Check for managed identity
        if os.environ.get("MSI_ENDPOINT") or os.environ.get("IDENTITY_ENDPOINT"):
            return AuthMethod.MANAGED_IDENTITY

        # Default to CLI auth
        return AuthMethod.CLI

    def authenticate_oidc(self) -> AzureCredentials:
        """Authenticate using GitHub OIDC.

        TODO: Implement full OIDC token exchange with Azure AD.

        Returns:
            AzureCredentials with OIDC token.

        Raises:
            NotImplementedError: OIDC auth not yet implemented.
        """
        # TODO: Implement OIDC token exchange
        # 1. Get OIDC token from GitHub using ACTIONS_ID_TOKEN_REQUEST_TOKEN
        # 2. Exchange token with Azure AD for access token
        # 3. Return credentials with token
        raise NotImplementedError(
            "OIDC authentication is not yet implemented. "
            "As a workaround, use the 'azure/login' action before calling avm-action. "
            "See docs/architecture.md for planned implementation."
        )

    def authenticate_service_principal(self) -> AzureCredentials:
        """Authenticate using a service principal.

        TODO: Implement full service principal authentication.

        Returns:
            AzureCredentials with client secret.

        Raises:
            NotImplementedError: Service principal auth not yet implemented.
        """
        # TODO: Implement service principal authentication
        # 1. Read client secret from environment
        # 2. Validate credentials
        # 3. Return credentials
        client_secret = os.environ.get("AZURE_CLIENT_SECRET") or os.environ.get(
            "ARM_CLIENT_SECRET"
        )

        if not client_secret:
            raise ValueError(
                "Service principal authentication requires AZURE_CLIENT_SECRET "
                "or ARM_CLIENT_SECRET environment variable."
            )

        return AzureCredentials(
            subscription_id=self.subscription_id,
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=client_secret,
            auth_method=AuthMethod.SERVICE_PRINCIPAL,
        )

    def authenticate_cli(self) -> AzureCredentials:
        """Authenticate using Azure CLI credentials.

        This assumes the user has already logged in with `az login`.

        Returns:
            AzureCredentials for CLI authentication.
        """
        return AzureCredentials(
            subscription_id=self.subscription_id,
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            auth_method=AuthMethod.CLI,
        )

    def authenticate(self) -> AzureCredentials:
        """Authenticate with Azure using the detected method.

        Returns:
            AzureCredentials based on the detected auth method.

        Raises:
            NotImplementedError: For auth methods not yet implemented.
        """
        method = self.detect_auth_method()

        if method == AuthMethod.OIDC:
            return self.authenticate_oidc()
        elif method == AuthMethod.SERVICE_PRINCIPAL:
            return self.authenticate_service_principal()
        elif method == AuthMethod.MANAGED_IDENTITY:
            # TODO: Implement managed identity authentication
            raise NotImplementedError(
                "Managed Identity authentication not yet implemented. "
                "As a workaround, use the 'azure/login' action with managed identity, "
                "or use CLI authentication by running 'az login' first."
            )
        else:
            return self.authenticate_cli()

    def set_terraform_env_vars(self, credentials: AzureCredentials) -> dict:
        """Generate environment variables for Terraform Azure provider.

        Args:
            credentials: The Azure credentials.

        Returns:
            Dictionary of environment variables for Terraform.
        """
        env_vars = {
            "ARM_SUBSCRIPTION_ID": credentials.subscription_id,
            "ARM_TENANT_ID": credentials.tenant_id,
        }

        if credentials.client_id:
            env_vars["ARM_CLIENT_ID"] = credentials.client_id

        if credentials.client_secret:
            env_vars["ARM_CLIENT_SECRET"] = credentials.client_secret

        if credentials.token:
            env_vars["ARM_OIDC_TOKEN"] = credentials.token
            env_vars["ARM_USE_OIDC"] = "true"

        return env_vars


def create_authenticator_from_env() -> AzureAuthenticator | None:
    """Create an Azure authenticator from environment variables.

    Returns:
        AzureAuthenticator if Azure config is provided, None otherwise.
    """
    subscription_id = os.environ.get("INPUT_AZURE_SUBSCRIPTION_ID", "")
    tenant_id = os.environ.get("INPUT_AZURE_TENANT_ID", "")
    client_id = os.environ.get("INPUT_AZURE_CLIENT_ID", "")

    if not subscription_id or not tenant_id:
        return None

    return AzureAuthenticator(
        subscription_id=subscription_id,
        tenant_id=tenant_id,
        client_id=client_id,
    )
