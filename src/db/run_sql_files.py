# run_sql_files.py — Executes full database setup sequence

from pathlib import Path
import sys
import psycopg2
# Go two levels up (src/db → project root)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.db.connection import db_connection, check_connection, get_db_schema
from src.utils.logger import logger

SQL_DIR = PROJECT_ROOT / "src" / "sql"

FILES = [
    "01_schema.sql",
    #"02_seed.sql",
    #"03_indexes.sql",
    #"04_functions.sql",
    #"05_testdata.sql",
]
check_connection()
logger.info(f"Loading the following files to DB {FILES}")


def run_sql_file(conn, path):
    with conn.cursor() as cur, open(path, "r", encoding="utf-8") as f:
        cur.execute(f.read())
    conn.commit()

def main():
    conn = db_connection()
    for fname in FILES:
        try:
            run_sql_file(conn, SQL_DIR / fname)
            logger.info(f'Ran {fname} without errors')
        except psycopg2.Error as e:
            logger.info(e)
    conn.close()
    get_db_schema()

if __name__ == "__main__":
    main()