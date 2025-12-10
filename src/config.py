"""
config.py

Load environment variables from the .env file and expose them as module-level constants.

Features:
- resolves absolute path to .env regardless of current working directory
- logs source path for transparency
- provides defaults ("failed_to_fetch") if variables are missing
"""


# Stdlib imports
import os
from pathlib import Path


# Third-party imports
from dotenv import load_dotenv


# Internal imports
from src.utils.logger import logger


# Path resolution
PROJECT_ROOT = Path(__file__).resolve().parents[1]
env_path = PROJECT_ROOT / ".env"

# Build relative path for cleaner log output
rel_path = (
    env_path.relative_to(PROJECT_ROOT.parent)
    if env_path.exists()
    else env_path.name
)

logger.info(f"Loading environment variables from {rel_path}")


# Load environment
load_dotenv(dotenv_path=env_path)


# Database configuration
DB_NAME = os.getenv("DB_NAME", "failed_to_fetch")
DB_USER = os.getenv("DB_USER", "failed_to_fetch")
DB_PASSWORD = os.getenv("DB_PASSWORD", "failed_to_fetch")
DB_HOST = os.getenv("DB_HOST", "failed_to_fetch")
DB_HOST_PORT = int(os.getenv("DB_HOST_PORT", 0))


# Container/VM configuration
COLIMA_PROFILE = os.getenv("COLIMA_PROFILE", "failed_to_fetch")
DOCKER_PROFILE = os.getenv("DOCKER_PROFILE", "failed_to_fetch")