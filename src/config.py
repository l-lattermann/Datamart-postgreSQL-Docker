# Loads the Environment Variables from the .env file and provides access to configuration settings

from pathlib import Path
from dotenv import load_dotenv
import os

# --- Load environment variables ---
# Resolve absolute path so it works from any working directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# --- Read config ---
DB_NAME = os.getenv("DB_NAME", "default_profile")
DB_USER = os.getenv("DB_USER", "default_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "default_pass")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_HOST_PORT = int(os.getenv("DB_HOST_PORT", "0000"))

