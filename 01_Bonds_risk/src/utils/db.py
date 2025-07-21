import psycopg2
from psycopg2.extras import execute_values
from src.config import DB_CONFIG

def get_conn():
    """
    Opens a new PostgreSQL connection using values from DB_CONFIG.
    You MUST close it (or use 'with') after use.
    """
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )

def test_connection():
    """
    Simple sanity test: opens connection, runs SELECT 1, returns True if OK.
    """
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        return True
    except Exception as e:
        print("Connection FAILED:", e)
        return False

def bulk_insert(table: str, columns: list[str], rows: list[tuple]):
    """
    Efficiently insert many rows.
    table: table name as string
    columns: list of column names
    rows: list of tuples with values
    """
    if not rows:
        return
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES %s"
    with get_conn() as conn, conn.cursor() as cur:
        execute_values(cur, sql, rows)
        conn.commit()

def insert_bond(isin: str,
                issuer: str,
                issue_date: str,
                maturity_date: str,
                coupon_rate: float,
                coupon_frequency: int,
                face_value: float,
                credit_rating: str):
    """
    Insert a single bond row into the 'bonds' table.

    All dates passed as 'YYYY-MM-DD' strings.
    coupon_rate = percentage (e.g. 5.25 means 5.25%)
    coupon_frequency = 1 (annual) or 2 (semiannual)
    """
    sql = """
    INSERT INTO bonds (
        isin, issuer, issue_date, maturity_date,
        coupon_rate, coupon_frequency, face_value, credit_rating
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    values = (
        isin,
        issuer,
        issue_date,
        maturity_date,
        coupon_rate,
        coupon_frequency,
        face_value,
        credit_rating
    )
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, values)
        conn.commit()
    print(f"Bond {isin} inserted successfully.")


if __name__ == "__main__":
    print("Testing database connection...")
    print("Connection successful?", test_connection())

    # Insert a single sample bond (only once)
    insert_bond(
        isin="IN00000001",
        issuer="Alpha Capital",
        issue_date="2020-01-01",
        maturity_date="2030-01-01",
        coupon_rate=5.25,        # percent
        coupon_frequency=2,      # semiannual
        face_value=1000.00,
        credit_rating="AAA"
    )
