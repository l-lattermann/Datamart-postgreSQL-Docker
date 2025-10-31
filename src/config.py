# Loads the Environment Variables from the .env file and provides access to configuration settings

from pathlib import Path
from dotenv import load_dotenv
import os
from src.utils.logger import logger

# Resolve absolute path so it works from any working directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]
env_path = Path(__file__).resolve().parents[1] / '.env'
rel_path = env_path.relative_to(PROJECT_ROOT.parent) if env_path.exists() else env_path.name
logger.info(f"Loading env variables from {rel_path}")

# --- Load environment variables ---
load_dotenv(dotenv_path=env_path)

# --- Read config ---
DB_NAME = os.getenv('DB_NAME','failed_to_fetch')
DB_USER = os.getenv('DB_USER','failed_to_fetch')
DB_PASSWORD = os.getenv('DB_PASSWORD','failed_to_fetch')
DB_HOST = os.getenv('DB_HOST','failed_to_fetch')
DB_HOST_PORT = int(os.getenv('DB_HOST_PORT', 0000))

COLIMA_PROFILE = os.getenv('COLIMA_PROFILE' ,'failed_to_fetch')
DOCKER_PROFILE = os.getenv('DOCKER_PROFILE','failed_to_fetch')
