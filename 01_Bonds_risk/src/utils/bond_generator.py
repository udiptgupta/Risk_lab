import random
import datetime
from src.utils.db import insert_bond

def random_isin():
    # ISIN: 2 letters + 10 digits (simplified)
    letters = "IN"
    numbers = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    return letters + numbers

def random_date(start_year=2015, end_year=2024):
    """
    Pick a random calendar date between Jan 1 start_year and Dec 31 end_year.
    """
    start = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)
    delta_days = (end - start).days
    return start + datetime.timedelta(days=random.randint(0, delta_days))

def random_maturity(issue_date, min_years=5, max_years=20):
    """
    Safely add a random number of whole years to issue_date.
    If the same month/day doesn't exist (e.g. Feb 29 to non-leap year),
    fallback by reducing the day until valid.
    """
    years_to_add = random.randint(min_years, max_years)
    target_year = issue_date.year + years_to_add
    month = issue_date.month
    day = issue_date.day
    # Try the same month/day; if invalid (e.g. Feb 29), step day downward.
    while day > 28:
        try:
            return datetime.date(target_year, month, day)
        except ValueError:
            day -= 1
    # If we fall out of loop (very rare), just return last safe day
    return datetime.date(target_year, month, day)

def generate_random_bond():
    isin = random_isin()
    issuer = random.choice(["Alpha Capital", "BlueStone Corp", "Zenith Bank", "Aurora Finance"])
    issue_date = random_date()
    maturity_date = random_maturity(issue_date)
    coupon_rate = round(random.uniform(3.0, 8.0), 2)  # 3% to 8%
    coupon_frequency = random.choice([1, 2])  # annual or semiannual
    face_value = random.choice([1000, 5000, 10000])
    credit_rating = random.choice(["AAA", "AA", "A", "BBB"])
    return (isin, issuer, issue_date, maturity_date, coupon_rate, coupon_frequency, face_value, credit_rating)

def generate_bonds(n=1000):
    bonds = []
    for _ in range(n):
        bonds.append(generate_random_bond())
    return bonds

from src.utils.db import bulk_insert

if __name__ == "__main__":
    bonds = generate_bonds(1000)
    columns = [
        "isin", "issuer", "issue_date", "maturity_date",
        "coupon_rate", "coupon_frequency", "face_value", "credit_rating"
    ]
    bulk_insert("bonds", columns, bonds)
    print(f"{len(bonds)} bonds inserted successfully.")

