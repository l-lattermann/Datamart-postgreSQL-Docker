"""
conftest.py

Global pytest configuration for the project.

Features:
- ensures project root is in sys.path
- sets up logging to logs/test.log
- redirects stdout/stderr (print) to pytest capture
"""

# ---------------------------------------------------------------------------
# Stdlib imports
# ---------------------------------------------------------------------------
import os
import sys
import logging
import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# ---------------------------------------------------------------------------
# Pytest configuration
# ---------------------------------------------------------------------------
def pytest_configure(config):
    """
    Configure pytest logging and output capturing.
    """
    log_file = os.path.join("logs", "test.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        filename=log_file,
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Capture print() and stdout
    config.option.capture = "tee-sys"