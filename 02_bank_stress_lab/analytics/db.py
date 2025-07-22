# connection helpers
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv() #load .env file

DB_CONFIG = dict(
    host = os.getenv("DB_HOST"),
    port = os.getenv("DB_PORT"),
    dbname = os.getenv("DB_NAME"),
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASS")
)

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

if __name__ == "__main__":
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM banks;")
                print("Banks count:", cur.fetchone()[0])
    except Exception as e:
        print("Error:", e)
