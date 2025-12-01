"""Configuration module for AVM Action.

This module handles parsing and validation of GitHub Action inputs,
providing a typed configuration object for use throughout the action.
"""

import json
import os
from dataclasses import dataclass, field
from enum import Enum


class TerraformCommand(Enum):
    """Supported Terraform commands."""

    INIT = "init"
    VALIDATE = "validate"
    PLAN = "plan"
    APPLY = "apply"
    DESTROY = "destroy"


class LogLevel(Enum):
    """Supported log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class AzureConfig:
    """Azure authentication configuration.

    Attributes:
        subscription_id: Azure Subscription ID.
        tenant_id: Azure Tenant ID.
        client_id: Azure Client ID (optional; prefer OIDC).
    """

    subscription_id: str = ""
    tenant_id: str = ""
    client_id: str = ""

    def is_configured(self) -> bool:
        """Check if Azure configuration is provided.

        Returns:
            True if subscription_id and tenant_id are set.
        """
        return bool(self.subscription_id and self.tenant_id)


@dataclass
class ActionConfig:
    """Configuration for the AVM Action.

    This dataclass maps GitHub Action inputs to Python types,
    applying defaults and basic parsing.

    Attributes:
        tf_directory: Path to the Terraform configuration directory.
        tfvars_files: List of tfvars files.
        backend_config_file: Path to backend configuration file.
        command: Terraform command to execute.
        workspace: Terraform workspace name.
        azure: Azure authentication configuration.
        var_overrides: Dictionary of variable overrides.
        log_level: Logging level.
    """

    tf_directory: str = "."
    tfvars_files: list[str] = field(default_factory=list)
    backend_config_file: str = ""
    command: TerraformCommand = TerraformCommand.PLAN
    workspace: str = "default"
    azure: AzureConfig = field(default_factory=AzureConfig)
    var_overrides: dict[str, str] = field(default_factory=dict)
    log_level: LogLevel = LogLevel.INFO

    def validate(self) -> list[str]:
        """Validate the configuration.

        Returns:
            List of validation error messages. Empty list if valid.
        """
        errors: list[str] = []

        # Validate tf_directory
        if not self.tf_directory:
            errors.append("tf_directory cannot be empty")

        # Validate command is valid
        if not isinstance(self.command, TerraformCommand):
            errors.append(f"Invalid command: {self.command}")

        # Validate workspace name (basic check)
        if (
            self.workspace
            and not self.workspace.replace("-", "").replace("_", "").isalnum()
        ):
            errors.append(f"Invalid workspace name: {self.workspace}")

        return errors


def _parse_tfvars_files(value: str) -> list[str]:
    """Parse comma-separated tfvars files list.

    Args:
        value: Comma-separated string of file paths.

    Returns:
        List of file path strings.
    """
    if not value:
        return []
    return [f.strip() for f in value.split(",") if f.strip()]


def _parse_var_overrides(value: str) -> dict[str, str]:
    """Parse variable overrides from JSON or key=value format.

    Args:
        value: JSON string or key=value pairs separated by newlines/commas.

    Returns:
        Dictionary of variable overrides.
    """
    if not value:
        return {}

    # Try JSON first
    try:
        parsed = json.loads(value)
        if isinstance(parsed, dict):
            return {str(k): str(v) for k, v in parsed.items()}
    except json.JSONDecodeError:
        pass

    # Fall back to key=value parsing
    overrides: dict[str, str] = {}
    # Split by newlines or commas
    pairs = value.replace("\n", ",").split(",")
    for pair in pairs:
        pair = pair.strip()
        if "=" in pair:
            key, val = pair.split("=", 1)
            overrides[key.strip()] = val.strip()

    return overrides


def _parse_command(value: str) -> TerraformCommand:
    """Parse command string to TerraformCommand enum.

    Args:
        value: Command string.

    Returns:
        TerraformCommand enum value.

    Raises:
        ValueError: If command is not recognized.
    """
    value = value.lower().strip()
    try:
        return TerraformCommand(value)
    except ValueError as e:
        valid_commands = [c.value for c in TerraformCommand]
        raise ValueError(
            f"Invalid command '{value}'. Valid commands: {valid_commands}"
        ) from e


def _parse_log_level(value: str) -> LogLevel:
    """Parse log level string to LogLevel enum.

    Args:
        value: Log level string.

    Returns:
        LogLevel enum value.
    """
    value = value.upper().strip()
    try:
        return LogLevel(value)
    except ValueError:
        return LogLevel.INFO


def load_config_from_env() -> ActionConfig:
    """Load configuration from environment variables.

    GitHub Actions passes inputs via INPUT_* environment variables.

    Returns:
        Populated ActionConfig instance.
    """

    def get_input(name: str, default: str = "") -> str:
        """Get an input from environment with fallback to default."""
        return os.environ.get(f"INPUT_{name.upper()}", default)

    azure_config = AzureConfig(
        subscription_id=get_input("azure_subscription_id"),
        tenant_id=get_input("azure_tenant_id"),
        client_id=get_input("azure_client_id"),
    )

    command_str = get_input("command", "plan")
    log_level_str = get_input("log_level", "INFO")

    config = ActionConfig(
        tf_directory=get_input("tf_directory", "."),
        tfvars_files=_parse_tfvars_files(get_input("tfvars_files")),
        backend_config_file=get_input("backend_config_file"),
        command=_parse_command(command_str),
        workspace=get_input("workspace", "default"),
        azure=azure_config,
        var_overrides=_parse_var_overrides(get_input("var_overrides")),
        log_level=_parse_log_level(log_level_str),
    )

    return config
