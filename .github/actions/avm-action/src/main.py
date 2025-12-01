"""Main entry point for AVM Action.

This module orchestrates the GitHub Action execution by:
1. Loading configuration from environment variables.
2. Validating inputs.
3. Constructing and executing Terraform commands.
4. Setting action outputs.
"""

import sys

from .config import load_config_from_env
from .terraform_runner import TerraformRunner
from .utils.logging import github_error, github_output, setup_logging


def main() -> int:
    """Execute the AVM Action.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    # Set up logging
    logger = setup_logging()
    logger.info("Starting AVM Action")

    try:
        # Load configuration from environment
        logger.debug("Loading configuration from environment")
        config = load_config_from_env()

        # Validate configuration
        errors = config.validate()
        if errors:
            for error in errors:
                github_error(error)
                logger.error(f"Configuration error: {error}")
            return 1

        logger.info(
            f"Running Terraform {config.command.value} in {config.tf_directory}"
        )
        logger.debug(f"Workspace: {config.workspace}")
        logger.debug(f"tfvars files: {config.tfvars_files}")
        logger.debug(f"AVM version: {config.avm_version}")
        logger.debug(f"Terraform version: {config.terraform_version}")
        logger.debug(f"AzureRM provider version: {config.azurerm_version}")

        # Create Terraform runner
        # TODO: Remove dry_run=True when ready for production execution
        try:
            runner = TerraformRunner(config, dry_run=True)
        except RuntimeError as e:
            # Terraform not found - provide helpful message
            logger.warning(str(e))
            github_output("plan_output", "Terraform not installed - dry run mode")
            github_output("state_summary", "No state changes (dry run)")
            logger.info("Action completed in dry-run mode (Terraform not available)")
            return 0

        # Execute the command
        result = runner.run()

        # Set outputs
        github_output("plan_output", result.stdout)
        github_output("state_summary", f"Exit code: {result.return_code}")

        if result.return_code != 0:
            logger.error(
                f"Terraform command failed with exit code {result.return_code}"
            )
            if result.stderr:
                logger.error(f"Error output: {result.stderr}")
            return result.return_code

        logger.info("AVM Action completed successfully")
        return 0

    except ValueError as e:
        github_error(str(e))
        logger.error(f"Validation error: {e}")
        return 1
    except Exception as e:
        github_error(f"Unexpected error: {e}")
        logger.exception("Unexpected error occurred")
        return 1


if __name__ == "__main__":
    sys.exit(main())
