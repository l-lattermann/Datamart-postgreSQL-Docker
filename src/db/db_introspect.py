"""
db_introspect.py

Utility helpers to:
- list all tables in the current PostgreSQL schema
- fetch column metadata for each table into pandas DataFrames
- dump all table contents into raw lists and DataFrames

Assumptions:
- valid connection factory at src.db.connection.db_connection
- SQL statements defined in src.db.sql_repo
- logger configured at src.utils.logger
"""

# ---------------------------------------------------------------------------
# Stdlib imports
# ---------------------------------------------------------------------------
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------------------------
import pandas as pd
from psycopg2 import sql

# ---------------------------------------------------------------------------
# Path/bootstrap
# Go two levels up (src/db → project root) so imports work when run as script.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Internal imports
# ---------------------------------------------------------------------------
from src.db.connection import db_connection
from src.utils.logger import logger
from src.db import sql_repo as sqlrepo


# ---------------------------------------------------------------------------
# Table name discovery
# ---------------------------------------------------------------------------
def fetch_all_tbl_names():
    """
    Retrieve all table names from the target schema.

    Uses a single query defined in sql_repo.FETCH_ALL_TABLE_NAMES and returns
    a flattened, de-duplicated list of table names.
    """
    # Connect to database
    conn = db_connection()
    cur = conn.cursor()

    # Fetch list of all table names
    cur.execute(sqlrepo.FETCH_ALL_TABLE_NAMES)
    result = cur.fetchall()

    # Flatten and deduplicate
    table_name_list = list({item[0] for item in result})

    # Close cursor (connection intentionally left as in original logic)
    cur.close()

    # Return the table name list
    return table_name_list


# ---------------------------------------------------------------------------
# Schema metadata dump
# ---------------------------------------------------------------------------
def fetch_db_schema():
    """
    Retrieve all tables and their column metadata from the database.

    Returns:
        dict[str, pandas.DataFrame]: mapping table_name → column-metadata-DF
    """
    # Connect to database
    conn = db_connection()
    cur = conn.cursor()

    # Discover tables
    table_name_list = fetch_all_tbl_names()

    # Init dict: table_name → DataFrame
    table_df_dict = {table_name: None for table_name in table_name_list}

    # Fetch column metadata for each table
    for table_name in table_name_list:
        cur.execute(sqlrepo.FETCH_TABLE_METADATA, (table_name,))
        result = cur.fetchall()

        df_columns = ["attr_name", "data_type", "is_nullable", "default_value"]
        table_df_dict[table_name] = pd.DataFrame(data=result, columns=df_columns)

    # Close cursor (connection intentionally left as in original logic)
    cur.close()

    # Return mapping
    return table_df_dict


# ---------------------------------------------------------------------------
# Full database dump
# ---------------------------------------------------------------------------
def dump_database_contents():
    """
    Dump the contents of all discovered tables.

    Builds two dicts internally:
    - tbl_dump_dict: table_name → raw rows
    - tbl_dump_df_dict: table_name → DataFrame with index on first column

    The dicts are constructed to be consumed later in the pipeline.
    """
    # Connect to database
    conn = db_connection()
    cur = conn.cursor()

    # Fetch all table names
    table_name_list = fetch_all_tbl_names()

    # Dict for raw dumps
    tbl_dump_dict = {table_name: None for table_name in table_name_list}

    # Dict for DataFrame dumps
    tbl_dump_df_dict = {table: None for table in table_name_list}

    # Fetch content per table
    for table in table_name_list:
        query = sql.SQL(sqlrepo.DUMP_TABLE).format(sql.Identifier(table))
        cur.execute(query)
        result = cur.fetchall()

        # store raw rows
        tbl_dump_dict[table] = result

        # build DataFrame with column names
        column_names = [desc[0] for desc in cur.description]
        tbl_dump_df_dict[table] = (
            pd.DataFrame(columns=column_names, data=result).set_index(column_names[0])
        )

        # diagnostic output
        print(tbl_dump_df_dict[table])

    # Close cursor (connection intentionally left as in original logic)
    cur.close()

    # Return the dataframe dict for later use