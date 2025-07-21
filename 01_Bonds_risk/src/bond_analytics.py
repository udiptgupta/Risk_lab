# src/bond_analytics.py
from datetime import date
from src.utils.db import get_conn
from src.utils.market_data import get_latest_curve, get_yield_curve, get_credit_spread
import math

def price_and_duration(bond_id: int, as_of: date):
    """
    Returns dict with price, macaulay duration, modified duration, convexity, and cash_flows.
    """
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
    coupon_rate = float(coupon_rate)
    face_value = float(face_value)
    spread = float(get_credit_spread(rating) or 0.0)

    # If bond has matured before as_of date
    if maturity_date <= as_of:
        return {
            "price": 0.0,
            "macaulay_duration": 0.0,
            "modified_duration": 0.0,
            "convexity": 0.0,
            "cash_flows": []
        }

    curve_date = get_latest_curve(as_of)
    if not curve_date:
        raise ValueError(f"No yield curve available before {as_of}")
    curve = [(yr, float(yld)) for yr, yld in get_yield_curve(curve_date)]

    # Generate cash flows
    years = (maturity_date - as_of).days / 365.0
    coupon = face_value * (coupon_rate / freq)
    n_payments = int(years * freq)
    cash_flows = [(i / freq, coupon) for i in range(1, n_payments + 1)]

    if cash_flows:  # Add face value to last payment if list isn't empty
        cash_flows[-1] = (cash_flows[-1][0], cash_flows[-1][1] + face_value)

    price = 0.0
    weighted_sum = 0.0
    convexity_sum = 0.0

    for t, cf in cash_flows:
        y_rf = curve[-1][1]
        for yr, yld in curve:
            if t <= yr:
                y_rf = yld
                break
        r = y_rf + spread
        pv = cf * math.exp(-r * t)
        price += pv
        weighted_sum += t * pv
        convexity_sum += (t**2) * pv

    if price <= 0:
        return {
            "price": 0.0,
            "macaulay_duration": 0.0,
            "modified_duration": 0.0,
            "convexity": 0.0,
            "cash_flows": []
        }


    macaulay_duration = weighted_sum / price
    modified_duration = macaulay_duration  # same under continuous comp
    convexity = convexity_sum / price

    return {
        "price": round(price, 2),
        "macaulay_duration": round(macaulay_duration, 4),
        "modified_duration": round(modified_duration, 4),
        "convexity": round(convexity, 4),
        "cash_flows": [(round(t, 2), round(cf, 2), round(cf * math.exp(-(y_rf + spread) * t), 2))
                       for t, cf in cash_flows]
    }

if __name__ == "__main__":
    result = price_and_duration(1, date(2025, 7, 20))
    print(result)
