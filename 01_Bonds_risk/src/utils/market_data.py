# src/utils/market_data.py

from .db import get_conn
from datetime import date

def get_yield_curve(curve_date: date):
    """
    Fetches all tenor-yield pairs for the given curve_date.
    Returns a list of tuples like: [(1, 0.0310), (2, 0.0320), ...]
    """
    query = """
        SELECT EXTRACT(YEAR FROM tenor)::int AS years, yield
        FROM yield_curve
        WHERE curve_date = %s
        ORDER BY years;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (curve_date,))
            rows = cur.fetchall()
    return rows

def get_latest_curve(before_date: date):
    """
    Fetches the latest available curve (on or before before_date).
    """
    query = """
        SELECT curve_date
        FROM yield_curve
        WHERE curve_date <= %s
        ORDER BY curve_date DESC
        LIMIT 1;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (before_date,))
            row = cur.fetchone()
    return row[0] if row else None

def get_credit_spread(rating: str):
    """
    Returns credit spread for a given rating in decimal form.
    (E.g., 150 bps -> 0.0150)
    """
    query = "SELECT spread_bps FROM credit_spread WHERE rating = %s;"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (rating,))
            row = cur.fetchone()
    return row[0] / 10000 if row else None

if __name__ == "__main__":
    # Quick smoke test
    latest_date = get_latest_curve(date(2025, 7, 20))
    print(f"Latest curve date: {latest_date}")
    print("Yield curve:", get_yield_curve(latest_date))
    print("Credit spread for A:", get_credit_spread('A'))
