# src/pricing_with_duration.py
from datetime import date
import math
from src.utils.db import get_conn
from src.utils.market_data import get_latest_curve, get_yield_curve, get_credit_spread


def price_and_duration(bond_id: int, as_of: date, debug=False):
    # 1. Fetch bond
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
    freq = int(freq)

    # 2. Get yield curve & spread
    curve_date = get_latest_curve(as_of)
    if not curve_date:
        raise ValueError(f"No curve before {as_of}")
    curve = [(int(y), float(r)) for y, r in get_yield_curve(curve_date)]
    spread = float(get_credit_spread(rating) or 0.0)

    def rf_yield_for_t(t):
        for yrs, y in curve:
            if t <= yrs:
                return y
        return curve[-1][1]

    # 3. Build cash flows
    years_to_mat = (maturity_date - as_of).days / 365.0
    n_payments = max(1, math.ceil(years_to_mat * freq))
    coupon_amt = face_value * (coupon_rate / freq)
    cash_flows = []
    for i in range(1, n_payments + 1):
        t = i / freq
        amt = coupon_amt
        if i == n_payments:
            amt += face_value
        cash_flows.append((t, amt))

    # 4. Price and duration
    price = 0.0
    weighted_sum = 0.0
    detailed = []
    for t, cf in cash_flows:
        r = rf_yield_for_t(t) + spread
        pv = cf * math.exp(-r * t)
        price += pv
        weighted_sum += t * pv
        detailed.append((t, cf, pv))

    macaulay = weighted_sum / price
    modified = macaulay  # continuous comp => same

    if debug:
        print(f"Bond {bond_id} | Price={price:.2f} | MacDur={macaulay:.4f} yrs")

    return {
        "price": round(price, 2),
        "macaulay_duration": round(macaulay, 4),
        "modified_duration": round(modified, 4),
        "cash_flows": detailed
    }


if __name__ == "__main__":
    result = price_and_duration(1, date(2025, 7, 20), debug=True)
    print(result)
