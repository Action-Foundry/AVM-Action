"""Terraform command runner for AVM Action.

This module provides functions to construct and execute Terraform commands.
Currently, actual subprocess execution is stubbed for safety; see TODOs for
extension points.
"""

import os
import shutil
import subprocess
from dataclasses import dataclass

from .config import ActionConfig, TerraformCommand


@dataclass
class CommandResult:
    """Result of a command execution.

    Attributes:
        return_code: Exit code from the command.
        stdout: Standard output from the command.
        stderr: Standard error from the command.
        command: The command that was executed.
    """

    return_code: int
    stdout: str
    stderr: str
    command: list[str]


class TerraformRunner:
    """Runner for Terraform commands.

    This class handles the construction and execution of Terraform commands
    based on the action configuration.

    Attributes:
        config: The action configuration.
        terraform_path: Path to the Terraform binary.
        dry_run: If True, commands are not actually executed.
    """

    def __init__(
        self,
        config: ActionConfig,
        terraform_path: str | None = None,
        dry_run: bool = True,
    ):
        """Initialize the Terraform runner.

        Args:
            config: Action configuration.
            terraform_path: Optional path to Terraform binary.
            dry_run: If True, don't actually execute commands (default: True).
        """
        self.config = config
        self.terraform_path = terraform_path or self._find_terraform()
        self.dry_run = dry_run

    def _find_terraform(self) -> str:
        """Find the Terraform binary in PATH.

        Returns:
            Path to Terraform binary.

        Raises:
            RuntimeError: If Terraform is not found.
        """
        terraform = shutil.which("terraform")
        if terraform:
            return terraform
        # TODO: Support Terraform installation or download
        raise RuntimeError(
            "Terraform binary not found in PATH. "
            "Please ensure Terraform is installed."
        )

    def build_init_command(self) -> list[str]:
        """Build the terraform init command.

        Returns:
            List of command arguments.
        """
        cmd = [self.terraform_path, "init", "-input=false"]

        if self.config.backend_config_file:
            cmd.append(f"-backend-config={self.config.backend_config_file}")

        return cmd

    def build_validate_command(self) -> list[str]:
        """Build the terraform validate command.

        Returns:
            List of command arguments.
        """
        return [self.terraform_path, "validate"]

    def build_plan_command(self, out_file: str | None = None) -> list[str]:
        """Build the terraform plan command.

        Args:
            out_file: Optional path to save the plan file.

        Returns:
            List of command arguments.
        """
        cmd = [self.terraform_path, "plan", "-input=false"]

        # Add tfvars files
        for tfvar_file in self.config.tfvars_files:
            cmd.append(f"-var-file={tfvar_file}")

        # Add variable overrides
        for key, value in self.config.var_overrides.items():
            cmd.append(f"-var={key}={value}")

        if out_file:
            cmd.append(f"-out={out_file}")

        return cmd

    def build_apply_command(self, plan_file: str | None = None) -> list[str]:
        """Build the terraform apply command.

        Args:
            plan_file: Optional path to a saved plan file.

        Returns:
            List of command arguments.
        """
        cmd = [self.terraform_path, "apply", "-input=false", "-auto-approve"]

        if plan_file:
            cmd.append(plan_file)
        else:
            # Add tfvars files if not using a plan file
            for tfvar_file in self.config.tfvars_files:
                cmd.append(f"-var-file={tfvar_file}")

            # Add variable overrides
            for key, value in self.config.var_overrides.items():
                cmd.append(f"-var={key}={value}")

        return cmd

    def build_destroy_command(self) -> list[str]:
        """Build the terraform destroy command.

        Returns:
            List of command arguments.
        """
        cmd = [self.terraform_path, "destroy", "-input=false", "-auto-approve"]

        # Add tfvars files
        for tfvar_file in self.config.tfvars_files:
            cmd.append(f"-var-file={tfvar_file}")

        # Add variable overrides
        for key, value in self.config.var_overrides.items():
            cmd.append(f"-var={key}={value}")

        return cmd

    def build_workspace_command(self) -> list[str]:
        """Build the terraform workspace select command.

        Returns:
            List of command arguments.
        """
        return [
            self.terraform_path,
            "workspace",
            "select",
            "-or-create=true",
            self.config.workspace,
        ]

    def build_command(self, command: TerraformCommand) -> list[str]:
        """Build a Terraform command based on the command type.

        Args:
            command: The Terraform command type.

        Returns:
            List of command arguments.
        """
        builders = {
            TerraformCommand.INIT: self.build_init_command,
            TerraformCommand.VALIDATE: self.build_validate_command,
            TerraformCommand.PLAN: self.build_plan_command,
            TerraformCommand.APPLY: self.build_apply_command,
            TerraformCommand.DESTROY: self.build_destroy_command,
        }

        builder = builders.get(command)
        if not builder:
            raise ValueError(f"Unsupported command: {command}")

        return builder()

    def run_command(self, cmd: list[str]) -> CommandResult:
        """Execute a Terraform command.

        Args:
            cmd: List of command arguments.

        Returns:
            CommandResult with execution results.

        Note:
            If dry_run is True, the command is not actually executed.
            TODO: Implement full subprocess execution for production use.
        """
        if self.dry_run:
            # TODO: Remove dry_run mode and implement full execution
            # This is intentionally stubbed for initial PR safety
            return CommandResult(
                return_code=0,
                stdout=f"[DRY RUN] Would execute: {' '.join(cmd)}",
                stderr="",
                command=cmd,
            )

        # Change to the Terraform directory
        original_dir = os.getcwd()
        try:
            os.chdir(self.config.tf_directory)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            return CommandResult(
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                command=cmd,
            )
        finally:
            os.chdir(original_dir)

    def run(self) -> CommandResult:
        """Run the configured Terraform command.

        This method handles workspace selection and command execution.

        Returns:
            CommandResult with execution results.
        """
        # Select workspace if not default
        if self.config.workspace and self.config.workspace != "default":
            workspace_cmd = self.build_workspace_command()
            workspace_result = self.run_command(workspace_cmd)
            if workspace_result.return_code != 0:
                return workspace_result

        # Build and run the main command
        cmd = self.build_command(self.config.command)
        return self.run_command(cmd)
