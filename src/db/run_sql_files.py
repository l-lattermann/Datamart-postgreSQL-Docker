# Stdlib imports
from pathlib import Path
import sys

# Third-party imports
import psycopg2

# Path/bootstrap
# Go two levels up (src/db → project root) so src.* imports work.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# Internal imports
from src.db.connection import db_connection, check_connection
from src.db.utils.db_introspect import fetch_db_schema_DfOutput
from src.utils.logger import logger



# SQL configuration
SQL_DIR = PROJECT_ROOT / "src" / "sql"

FILES = [
    "01_schema.sql",
    "02_seed.sql"
]

# initial connectivity check, keep logic as-is
check_connection()
logger.info(f"Loading the following files to DB {FILES}")



# helpers
def run_sql_file(conn, path: Path):
    """
    Execute the full contents of a .sql file in one cursor/transaction.
    Commits after successful execution.
    """
    with conn.cursor() as cur, open(path, "r", encoding="utf-8") as f:
        cur.execute(f.read())
    conn.commit()



# main routine
def main():
    conn = db_connection()
    for fname in FILES:
        try:
            run_sql_file(conn, SQL_DIR / fname)
            logger.info(f"Ran {fname} without errors")
        except psycopg2.Error as e:
            logger.info(e)
    conn.close()

    # run schema introspection at the end
    fetch_db_schema_DfOutput()



# CLI entrypoint
if __name__ == "__main__":
    main()