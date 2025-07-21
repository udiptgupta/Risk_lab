# src/pricing.py
from datetime import date
from src.utils.db import get_conn
from src.utils.market_data import get_latest_curve, get_yield_curve, get_credit_spread
import math

def price_bond(bond_id: int, as_of: date):
    """
    Calculate the price of a given bond_id as of a certain date.
    Assumes continuous compounding.
    """
    # 1. Fetch bond details
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT issue_date, maturity_date, coupon_rate, coupon_frequency,
                       face_value, credit_rating
                FROM bonds
                WHERE bond_id = %s;
            """, (bond_id,))
            bond = cur.fetchone()

    if not bond:
        raise ValueError(f"No bond found with id {bond_id}")

    issue_date, maturity_date, coupon_rate, freq, face_value, rating = bond

    # Ensure all numeric values are float
    coupon_rate = float(coupon_rate)
    face_value = float(face_value)
    freq = int(freq)

    # 2. Get the latest curve <= as_of
    curve_date = get_latest_curve(as_of)
    if not curve_date:
        raise ValueError(f"No yield curve available before {as_of}")
    curve = [(int(yr), float(yld)) for yr, yld in get_yield_curve(curve_date)]

    # Credit spread
    spread = float(get_credit_spread(rating) or 0.0)

    # 3. Generate cash flows
    cash_flows = []
    years = (maturity_date - as_of).days / 365.0
    coupon = face_value * (coupon_rate / freq)

    n_payments = int(years * freq)
    for i in range(1, n_payments + 1):
        t = i / freq
        cash_flows.append((t, coupon))
    # Add face value
    cash_flows[-1] = (cash_flows[-1][0], cash_flows[-1][1] + face_value)

    # 4. Discount cash flows
    price = 0.0
    for t, cf in cash_flows:
        y_rf = curve[-1][1]  # default to last tenor
        for yr, yld in curve:
            if t <= yr:
                y_rf = yld
                break
        r = y_rf + spread
        price += float(cf) * math.exp(-r * t)

    return round(price, 2)

if __name__ == "__main__":
    test_price = price_bond(1, date(2025, 7, 20))
    print(f"Bond 1 price: {test_price}")
