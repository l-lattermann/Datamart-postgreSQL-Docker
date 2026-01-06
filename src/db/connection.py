"""
connection.py

Database connection utilities for PostgreSQL.

Provides:
- db_connection(): returns a psycopg2 connection using src.config credentials
- check_connection(): verifies connectivity and logs result

Assumptions:
- src.config defines DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_HOST_PORT
- src.utils.logger is a configured logger
"""
# Stdlib imports
import sys
from pathlib import Path

# Third-party imports
import psycopg2
from psycopg2 import OperationalError

# Path/bootstrap
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# Internal imports
from src import config
from src.utils.logger import logger



# Connection factory
def db_connection():
    """
    Return a psycopg2 connection using credentials from src.config.
    """
    return psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_HOST_PORT,
    )



# Connection test
def check_connection() -> bool:
    """
    Try to establish a connection and execute a simple test query (SELECT 1).

    Returns:
        True  – if database responds correctly
        False – if connection or query fails
    """
    conn = None
    try:
        conn = db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()
            assert result == (1,), "Unexpected DB response"
        logger.info("Database connection OK.")
        return True

    except (AssertionError, OperationalError, psycopg2.Error) as e:
        logger.error(f"Database connection failed: {e}")
        return False

    finally:
        if conn is not None:
            conn.close()