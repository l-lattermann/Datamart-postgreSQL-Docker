import psycopg2

# Go two levels up (src/db → project root)
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from psycopg2 import OperationalError
from src.utils.logger import logger


def db_connection():
    return psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_HOST_PORT,
    )


def check_connection():
    conn = db_connection()
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

def get_db_schema():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position;
    """)

    logger.info("The datbase schema is:")
    result = cur.fetchall()
    if result:
        for row in result:
            logger.info(row)
        conn.close()
    else:
        logger.info('NONE')