import psycopg2
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
DB_PORT = int(os.getenv("DB_PORT", "5432"))

# --- Example usage ---
if __name__ == "__main__":
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Connected to PostgreSQL")
        print()

        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM listings;")
                print("Before test insert:", cur.fetchall())

                cur.execute("SAVEPOINT test;")
                cur.execute("CREATE TABLE IF NOT EXISTS listings (id SERIAL PRIMARY KEY, name TEXT);")
                cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public';")
                print("Created Tables:", cur.fetchall())
                
                cur.execute("INSERT INTO listings (name) VALUES (%s) RETURNING id;", ("Test Listing",))
                print("Inserted:", cur.fetchone()[0])
                cur.execute("SELECT * FROM listings;")
                print("Before rollback:", cur.fetchall())

                cur.execute("ROLLBACK TO SAVEPOINT test;")   
                cur.execute("RELEASE SAVEPOINT test;")       

                cur.execute("SELECT * FROM listings;")
                print("After rollback:", cur.fetchall())
                print()

    except Exception as e:
        print("Error:", e)

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()