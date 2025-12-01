"""Pytest configuration and shared fixtures for AVM Action tests."""

import os
import sys

# Add the action src to the Python path for all tests
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "../.github/actions/avm-action")
)
