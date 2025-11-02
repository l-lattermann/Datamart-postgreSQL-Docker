"""
sql_repo.py

Central store for SQL statements used by the DB introspection/utilities.

Notes:
- keep statements generic and information_schema-based
- do not embed dynamic identifiers directly; use psycopg2.sql for that
"""

# ---------------------------------------------------------------------------
# list all tables in public schema
# ---------------------------------------------------------------------------
FETCH_ALL_TABLE_NAMES = """
    SELECT table_name
    FROM information_schema.columns
    WHERE table_schema = 'public';
"""

# ---------------------------------------------------------------------------
# column metadata for a single table
# must match the column order expected by the callers
# ---------------------------------------------------------------------------
FETCH_TABLE_METADATA = """
    SELECT
        column_name,
        data_type,
        is_nullable,
        column_default
    FROM information_schema.columns
    WHERE table_name = %s;
"""

# ---------------------------------------------------------------------------
# dump all rows from a given table (identifier is filled in by caller)
# ---------------------------------------------------------------------------
DUMP_TABLE = """
    SELECT *
    FROM {};
"""