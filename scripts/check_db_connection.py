#!/usr/bin/env python3
import sys
from pathlib import Path
# Go two levels up (src/db → project root)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from src.db.connection import check_connection, get_db_schema
from src.utils.logger import logger

if __name__ == "__main__":
    ok = check_connection()
    get_db_schema()  
    sys.exit(0 if ok else 1)