# create banks + loans
import random
from analytics.db import get_conn
from psycopg2.extras import execute_values

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

def fetch_banks():
    sql = "SELECT bank_id , bank_name FROM banks ORDER by bank_id;"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
        
def generate_loans_for_bank(bank_id, n_loans = 10, default_prob = 0.05):
    rows = []
    #we'll fill rows with tuples
    seg_codes = ['Retail', 'Corporate', 'SME', 'Agri', 'Mortgage']
    for _ in range(n_loans):
        orig_amt = random.uniform(10000, 5000000)
        current_bal = orig_amt * random.uniform(0.5, 1.0)
        default_flag = random.random() < default_prob
        risk_weight = 1.0 if default_flag else 0.5
        seg_code = random.choice(seg_codes)
        rows.append((bank_id, orig_amt, current_bal, default_flag, risk_weight, seg_code))
    return rows

def bulk_insert_loans(rows):
    sql = """
          INSERT INTO loan_portfolio
          (bank_id, orig_amt, current_bal, default_flag, risk_weight, seg_code)
          VALUES %s
          """
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows)

if __name__ == "__main__":
    banks = fetch_banks()
    all_rows = []
    for bank_id, bank_name in banks:
        rows = generate_loans_for_bank(bank_id, n_loans = 500)
        all_rows.extend(rows)
    bulk_insert_loans(all_rows)
    print(f"Inserted {len(all_rows)} loans.")
