"""
conftest.py

Pytest configuration: unified logging setup.
Creates logs/test.log and attaches a single file handler to the root logger.
Prevents duplicate handlers on test reload.
"""

# ---------------------------------------------------------------------------
# Stdlib imports
# ---------------------------------------------------------------------------
import os
import logging


# ---------------------------------------------------------------------------
# Pytest configuration
# ---------------------------------------------------------------------------
def pytest_configure(config):
    """
    Configure pytest logging to write all output into logs/test.log.
    """
    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", "test.log")

    # root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # prevent duplicate handlers on reload
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(file_handler)