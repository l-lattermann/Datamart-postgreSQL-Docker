"""
db_helpers.py

Utility functions for database operations, including:
- printing all rows from a specified table for debugging purposes.
"""


# Internal imports
from src.db.connection import db_connection



# Function
def get_tbl_contents_as_str(table_name: str) -> str:
    """
    Connects to the database, retrieves all rows from the specified table,
    and returns a formatted string.

    Args:
        table_name (str): name of the table to print.

    Returns:
        str: formatted string containing all table rows.
    """
    conn = db_connection()
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM {table_name};")
    rows = cur.fetchall()

    result_string = f"Table: {table_name}\n"
    for row in rows:
        result_string += f"{row}\n"

    cur.close()
    conn.close()

    return result_string