# create banks + loans
import random
from datetime import datetime, timedelta
from analytics.db import get_conn
from psycopg2.extras import execute_values

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

START_DATE = datetime(2025, 7, 1)
NUM_DAYS = 90
LOANS_PER_BANK_PER_DAY = 50

SPIKE_PROB_PER_DAY = 0.2 #20% chance that a bank has a spike that day
SPIKE_MULTIPLIER_RANGE = (2,5) # Multiplier range (eg, 2x to 5x loans)

def fetch_banks():
    sql = "SELECT bank_id , bank_name FROM banks ORDER by bank_id;"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
        
def generate_loans_for_day(bank_id, loan_date, n_loans = LOANS_PER_BANK_PER_DAY, default_prob = 0.05):
    rows = []
    #we'll fill rows with tuples
    seg_codes = ['Retail', 'Corporate', 'SME', 'Agri', 'Mortgage']
    for _ in range(n_loans):
        orig_amt = random.uniform(10000, 5000000)
        current_bal = orig_amt * random.uniform(0.5, 1.0)
        default_flag = random.random() < default_prob
        risk_weight = 1.0 if default_flag else 0.5
        seg_code = random.choice(seg_codes)
        rows.append((bank_id, orig_amt, current_bal, default_flag, risk_weight, seg_code, loan_date))
    return rows

def bulk_insert_loans(rows):
    sql = """
          INSERT INTO loan_portfolio
          (bank_id, orig_amt, current_bal, default_flag, risk_weight, seg_code, loan_date)
          VALUES %s
          """
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows)

def simulate_loans_for_all_days():
    banks = fetch_banks()
    total_rows = 0
    for day in range(NUM_DAYS):
        loan_date = START_DATE + timedelta(days = day)
        daily_rows = []

        for bank_id, bank_name in banks:
            #Determine if today is a spike day for this bank
            if random.random() < SPIKE_PROB_PER_DAY:
                multiplier = random.randint(*SPIKE_MULTIPLIER_RANGE)
                loan_count = LOANS_PER_BANK_PER_DAY*multiplier
                print(f"Spike! {bank_name} has {loan_count} loans on {loan_date.date()} (x{multiplier})")
            else:
                loan_count = LOANS_PER_BANK_PER_DAY

            daily_rows.extend(generate_loans_for_day(bank_id, loan_date, n_loans = loan_count))

        bulk_insert_loans(daily_rows)
        total_rows += len(daily_rows)
        print(f"(\{loan_date.date()} → {len(daily_rows)} loans inserted.")

    print(f"\n Done. Inserted {total_rows} loans over {NUM_DAYS} days.")

if __name__ == "__main__":
    simulate_loans_for_all_days()
