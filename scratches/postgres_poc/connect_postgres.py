import psycopg2

# Connection parameters (match your docker-compose.yml)
DB_NAME = "test_db"
DB_USER = "lau"
DB_PASSWORD = "123"
DB_HOST = "localhost"
DB_PORT = "5432"

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    print("Connected to PostgreSQL")

    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS listings (id SERIAL PRIMARY KEY, name TEXT);")
    cur.execute("INSERT INTO listings (name) VALUES (%s) RETURNING id;", ("Test Listing",))
    new_id = cur.fetchone()[0]
    conn.commit()

    cur.execute("SELECT * FROM listings;")
    rows = cur.fetchall()
    print("Rows:", rows)

except Exception as e:
    print("Error:", e)

finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()