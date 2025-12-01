"""Logging utilities for AVM Action."""

import logging
import os
import sys


def setup_logging(level: str | None = None) -> logging.Logger:
    """Set up and configure logging for the action.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR).
               Defaults to INFO if not specified.

    Returns:
        Configured logger instance.
    """
    log_level = level or os.environ.get("INPUT_LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logger = logging.getLogger("avm-action")
    logger.setLevel(numeric_level)

    return logger


def github_output(name: str, value: str) -> None:
    """Write an output to GitHub Actions output file.

    Args:
        name: The name of the output variable.
        value: The value to set for the output.
    """
    github_output_file = os.environ.get("GITHUB_OUTPUT")
    if github_output_file:
        with open(github_output_file, "a", encoding="utf-8") as f:
            # Handle multiline values
            if "\n" in value:
                delimiter = "EOF"
                f.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")
            else:
                f.write(f"{name}={value}\n")
    else:
        # Fallback for local testing
        print(f"::set-output name={name}::{value}")


def github_error(message: str) -> None:
    """Print an error message in GitHub Actions format.

    Args:
        message: The error message to display.
    """
    print(f"::error::{message}")


def github_warning(message: str) -> None:
    """Print a warning message in GitHub Actions format.

    Args:
        message: The warning message to display.
    """
    print(f"::warning::{message}")


def github_notice(message: str) -> None:
    """Print a notice message in GitHub Actions format.

    Args:
        message: The notice message to display.
    """
    print(f"::notice::{message}")
