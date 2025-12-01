"""Unit tests for terraform_runner module."""

import os
import sys

import pytest

# Add the action src to path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "../../.github/actions/avm-action")
)

from src.config import ActionConfig, TerraformCommand
from src.terraform_runner import CommandResult, TerraformRunner


class TestCommandResult:
    """Tests for CommandResult dataclass."""

    def test_creation(self):
        """CommandResult should be created correctly."""
        result = CommandResult(
            return_code=0,
            stdout="output",
            stderr="error",
            command=["terraform", "plan"],
        )
        assert result.return_code == 0
        assert result.stdout == "output"
        assert result.stderr == "error"
        assert result.command == ["terraform", "plan"]


class TestTerraformRunner:
    """Tests for TerraformRunner class."""

    @pytest.fixture
    def basic_config(self):
        """Create a basic configuration for testing."""
        return ActionConfig(
            tf_directory="./terraform",
            command=TerraformCommand.PLAN,
            workspace="default",
        )

    @pytest.fixture
    def full_config(self):
        """Create a full configuration with all options for testing."""
        return ActionConfig(
            tf_directory="./terraform",
            tfvars_files=["dev.tfvars", "common.tfvars"],
            backend_config_file="backend.hcl",
            command=TerraformCommand.PLAN,
            workspace="development",
            var_overrides={"env": "dev", "count": "3"},
        )

    def test_build_init_command_basic(self, basic_config):
        """Build init command without backend config."""
        runner = TerraformRunner(
            basic_config, terraform_path="/usr/bin/terraform", dry_run=True
        )
        cmd = runner.build_init_command()

        assert cmd == ["/usr/bin/terraform", "init", "-input=false"]

    def test_build_init_command_with_backend(self, full_config):
        """Build init command with backend config."""
        runner = TerraformRunner(
            full_config, terraform_path="/usr/bin/terraform", dry_run=True
        )
        cmd = runner.build_init_command()

        assert cmd == [
            "/usr/bin/terraform",
            "init",
            "-input=false",
            "-backend-config=backend.hcl",
        ]

    def test_build_validate_command(self, basic_config):
        """Build validate command."""
        runner = TerraformRunner(
            basic_config, terraform_path="/usr/bin/terraform", dry_run=True
        )
        cmd = runner.build_validate_command()

        assert cmd == ["/usr/bin/terraform", "validate"]

    def test_build_plan_command_basic(self, basic_config):
        """Build plan command without options."""
        runner = TerraformRunner(
            basic_config, terraform_path="/usr/bin/terraform", dry_run=True
        )
        cmd = runner.build_plan_command()

        assert cmd == ["/usr/bin/terraform", "plan", "-input=false"]

    def test_build_plan_command_with_options(self, full_config):
        """Build plan command with tfvars and var overrides."""
        runner = TerraformRunner(
            full_config, terraform_path="/usr/bin/terraform", dry_run=True
        )
        cmd = runner.build_plan_command()

        assert "/usr/bin/terraform" in cmd
        assert "plan" in cmd
        assert "-input=false" in cmd
        assert "-var-file=dev.tfvars" in cmd
        assert "-var-file=common.tfvars" in cmd
        assert "-var=env=dev" in cmd
        assert "-var=count=3" in cmd

    def test_build_plan_command_with_out_file(self, basic_config):
        """Build plan command with output file."""
        runner = TerraformRunner(
            basic_config, terraform_path="/usr/bin/terraform", dry_run=True
        )
        cmd = runner.build_plan_command(out_file="plan.tfplan")

        assert "-out=plan.tfplan" in cmd

    def test_build_apply_command_basic(self, basic_config):
        """Build apply command without plan file."""
        runner = TerraformRunner(
            basic_config, terraform_path="/usr/bin/terraform", dry_run=True
        )
        cmd = runner.build_apply_command()

        assert cmd == [
            "/usr/bin/terraform",
            "apply",
            "-input=false",
            "-auto-approve",
        ]

    def test_build_apply_command_with_plan_file(self, basic_config):
        """Build apply command with plan file."""
        runner = TerraformRunner(
            basic_config, terraform_path="/usr/bin/terraform", dry_run=True
        )
        cmd = runner.build_apply_command(plan_file="plan.tfplan")

        assert "plan.tfplan" in cmd

    def test_build_apply_command_with_options(self, full_config):
        """Build apply command with tfvars and var overrides."""
        runner = TerraformRunner(
            full_config, terraform_path="/usr/bin/terraform", dry_run=True
        )
        cmd = runner.build_apply_command()

        assert "-var-file=dev.tfvars" in cmd
        assert "-var-file=common.tfvars" in cmd
        assert "-var=env=dev" in cmd

    def test_build_destroy_command(self, full_config):
        """Build destroy command with options."""
        runner = TerraformRunner(
            full_config, terraform_path="/usr/bin/terraform", dry_run=True
        )
        cmd = runner.build_destroy_command()

        assert "/usr/bin/terraform" in cmd
        assert "destroy" in cmd
        assert "-input=false" in cmd
        assert "-auto-approve" in cmd
        assert "-var-file=dev.tfvars" in cmd

    def test_build_workspace_command(self):
        """Build workspace select command."""
        config = ActionConfig(workspace="production")
        runner = TerraformRunner(
            config, terraform_path="/usr/bin/terraform", dry_run=True
        )
        cmd = runner.build_workspace_command()

        assert cmd == [
            "/usr/bin/terraform",
            "workspace",
            "select",
            "-or-create=true",
            "production",
        ]

    def test_build_command_dispatches_correctly(self, basic_config):
        """build_command should dispatch to correct builder."""
        runner = TerraformRunner(
            basic_config, terraform_path="/usr/bin/terraform", dry_run=True
        )

        assert "init" in runner.build_command(TerraformCommand.INIT)
        assert "validate" in runner.build_command(TerraformCommand.VALIDATE)
        assert "plan" in runner.build_command(TerraformCommand.PLAN)
        assert "apply" in runner.build_command(TerraformCommand.APPLY)
        assert "destroy" in runner.build_command(TerraformCommand.DESTROY)

    def test_run_command_dry_run(self, basic_config):
        """Dry run should not execute commands."""
        runner = TerraformRunner(
            basic_config, terraform_path="/usr/bin/terraform", dry_run=True
        )
        result = runner.run_command(["terraform", "plan"])

        assert result.return_code == 0
        assert "[DRY RUN]" in result.stdout
        assert "terraform plan" in result.stdout

    def test_run_executes_workspace_for_non_default(self):
        """Run should select workspace for non-default workspace."""
        config = ActionConfig(workspace="staging", command=TerraformCommand.PLAN)
        runner = TerraformRunner(
            config, terraform_path="/usr/bin/terraform", dry_run=True
        )
        result = runner.run()

        # In dry run mode, should still succeed
        assert result.return_code == 0
