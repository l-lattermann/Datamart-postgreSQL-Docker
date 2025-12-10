#!/usr/bin/env python3
"""
db_init.py

Minimal CLI utility to verify database connectivity and initialize schema inspection.

Features:
- Ensures PostgreSQL connection works via check_connection()
- Invokes get_db_schema() to introspect or create the database schema

Assumptions:
- src.db.connection.check_connection() exists and returns a boolean
- src.db.create_schema.get_db_schema() performs schema creation or inspection
"""


# Stdlib imports
import sys
from pathlib import Path


# Path/bootstrap
# Go one level up (src/db → project root) so imports work when run directly.

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


# Internal imports
from src.db.connection import check_connection
from src.db.utils.db_introspect import fetch_db_schema_list



# CLI entrypoint
if __name__ == "__main__":
    ok = check_connection()
    fetch_db_schema_list()
    sys.exit(0 if ok else 1)