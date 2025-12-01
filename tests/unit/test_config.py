"""Unit tests for config module."""

import os

# Add the action src to path
import sys
from unittest import mock

import pytest

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "../../.github/actions/avm-action")
)

from src.config import (
    ActionConfig,
    AzureConfig,
    LogLevel,
    TerraformCommand,
    _parse_command,
    _parse_log_level,
    _parse_tfvars_files,
    _parse_var_overrides,
    load_config_from_env,
)


class TestParseTfvarsFiles:
    """Tests for _parse_tfvars_files function."""

    def test_empty_string_returns_empty_list(self):
        """Empty string should return empty list."""
        assert _parse_tfvars_files("") == []

    def test_single_file(self):
        """Single file should be parsed correctly."""
        assert _parse_tfvars_files("dev.tfvars") == ["dev.tfvars"]

    def test_multiple_files(self):
        """Multiple comma-separated files should be parsed."""
        result = _parse_tfvars_files("dev.tfvars,prod.tfvars,common.tfvars")
        assert result == ["dev.tfvars", "prod.tfvars", "common.tfvars"]

    def test_files_with_spaces(self):
        """Files with spaces around commas should be trimmed."""
        result = _parse_tfvars_files("dev.tfvars , prod.tfvars , common.tfvars")
        assert result == ["dev.tfvars", "prod.tfvars", "common.tfvars"]

    def test_empty_entries_filtered(self):
        """Empty entries should be filtered out."""
        result = _parse_tfvars_files("dev.tfvars,,prod.tfvars,")
        assert result == ["dev.tfvars", "prod.tfvars"]


class TestParseVarOverrides:
    """Tests for _parse_var_overrides function."""

    def test_empty_string_returns_empty_dict(self):
        """Empty string should return empty dict."""
        assert _parse_var_overrides("") == {}

    def test_json_format(self):
        """JSON format should be parsed correctly."""
        result = _parse_var_overrides('{"key1": "value1", "key2": "value2"}')
        assert result == {"key1": "value1", "key2": "value2"}

    def test_key_value_format_single(self):
        """Single key=value should be parsed."""
        result = _parse_var_overrides("key1=value1")
        assert result == {"key1": "value1"}

    def test_key_value_format_multiple_comma(self):
        """Multiple comma-separated key=value should be parsed."""
        result = _parse_var_overrides("key1=value1,key2=value2")
        assert result == {"key1": "value1", "key2": "value2"}

    def test_key_value_format_multiple_newline(self):
        """Multiple newline-separated key=value should be parsed."""
        result = _parse_var_overrides("key1=value1\nkey2=value2")
        assert result == {"key1": "value1", "key2": "value2"}

    def test_value_with_equals_sign(self):
        """Values containing equals signs should be preserved."""
        result = _parse_var_overrides("key1=value=with=equals")
        assert result == {"key1": "value=with=equals"}


class TestParseCommand:
    """Tests for _parse_command function."""

    def test_valid_commands(self):
        """All valid commands should be parsed."""
        assert _parse_command("init") == TerraformCommand.INIT
        assert _parse_command("validate") == TerraformCommand.VALIDATE
        assert _parse_command("plan") == TerraformCommand.PLAN
        assert _parse_command("apply") == TerraformCommand.APPLY
        assert _parse_command("destroy") == TerraformCommand.DESTROY

    def test_case_insensitive(self):
        """Commands should be case-insensitive."""
        assert _parse_command("PLAN") == TerraformCommand.PLAN
        assert _parse_command("Plan") == TerraformCommand.PLAN

    def test_with_whitespace(self):
        """Commands with whitespace should be trimmed."""
        assert _parse_command("  plan  ") == TerraformCommand.PLAN

    def test_invalid_command_raises(self):
        """Invalid command should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            _parse_command("invalid")
        assert "Invalid command" in str(exc_info.value)


class TestParseLogLevel:
    """Tests for _parse_log_level function."""

    def test_valid_levels(self):
        """All valid log levels should be parsed."""
        assert _parse_log_level("DEBUG") == LogLevel.DEBUG
        assert _parse_log_level("INFO") == LogLevel.INFO
        assert _parse_log_level("WARNING") == LogLevel.WARNING
        assert _parse_log_level("ERROR") == LogLevel.ERROR

    def test_case_insensitive(self):
        """Log levels should be case-insensitive."""
        assert _parse_log_level("debug") == LogLevel.DEBUG
        assert _parse_log_level("Debug") == LogLevel.DEBUG

    def test_invalid_level_defaults_to_info(self):
        """Invalid log level should default to INFO."""
        assert _parse_log_level("invalid") == LogLevel.INFO


class TestAzureConfig:
    """Tests for AzureConfig class."""

    def test_is_configured_true(self):
        """is_configured should return True when subscription and tenant are set."""
        config = AzureConfig(
            subscription_id="sub-123",
            tenant_id="tenant-456",
        )
        assert config.is_configured() is True

    def test_is_configured_false_missing_subscription(self):
        """is_configured should return False when subscription_id is missing."""
        config = AzureConfig(
            subscription_id="",
            tenant_id="tenant-456",
        )
        assert config.is_configured() is False

    def test_is_configured_false_missing_tenant(self):
        """is_configured should return False when tenant_id is missing."""
        config = AzureConfig(
            subscription_id="sub-123",
            tenant_id="",
        )
        assert config.is_configured() is False


class TestActionConfig:
    """Tests for ActionConfig class."""

    def test_default_values(self):
        """Default values should be set correctly."""
        config = ActionConfig()
        assert config.tf_directory == "."
        assert config.tfvars_files == []
        assert config.backend_config_file == ""
        assert config.command == TerraformCommand.PLAN
        assert config.workspace == "default"
        assert config.var_overrides == {}
        assert config.log_level == LogLevel.INFO

    def test_validate_valid_config(self):
        """Valid config should return no errors."""
        config = ActionConfig(
            tf_directory="./terraform",
            command=TerraformCommand.PLAN,
            workspace="dev",
        )
        errors = config.validate()
        assert errors == []

    def test_validate_empty_tf_directory(self):
        """Empty tf_directory should produce an error."""
        config = ActionConfig(tf_directory="")
        errors = config.validate()
        assert "tf_directory cannot be empty" in errors

    def test_validate_invalid_workspace(self):
        """Invalid workspace name should produce an error."""
        config = ActionConfig(workspace="invalid workspace!")
        errors = config.validate()
        assert any("Invalid workspace name" in e for e in errors)


class TestLoadConfigFromEnv:
    """Tests for load_config_from_env function."""

    def test_loads_from_environment(self):
        """Config should be loaded from INPUT_* environment variables."""
        env = {
            "INPUT_TF_DIRECTORY": "./my-terraform",
            "INPUT_COMMAND": "apply",
            "INPUT_WORKSPACE": "production",
            "INPUT_TFVARS_FILES": "prod.tfvars,common.tfvars",
            "INPUT_LOG_LEVEL": "DEBUG",
        }
        with mock.patch.dict(os.environ, env, clear=False):
            config = load_config_from_env()

        assert config.tf_directory == "./my-terraform"
        assert config.command == TerraformCommand.APPLY
        assert config.workspace == "production"
        assert config.tfvars_files == ["prod.tfvars", "common.tfvars"]
        assert config.log_level == LogLevel.DEBUG

    def test_uses_defaults_when_not_set(self):
        """Default values should be used when env vars are not set."""
        env = {}
        with mock.patch.dict(os.environ, env, clear=True):
            config = load_config_from_env()

        assert config.tf_directory == "."
        assert config.command == TerraformCommand.PLAN
        assert config.workspace == "default"
