import random
from analytics.db import get_conn

def simulate_daily_deposits():
    print("⏳ Starting deposit simulation...")

    with get_conn() as conn:
        with conn.cursor() as cur:
            # Step 1: Fetch banks
            cur.execute("SELECT bank_id, total_deposits FROM banks;")
            banks = cur.fetchall()
            print(f"📌 Found {len(banks)} banks")

            # Step 2: Fetch loan dates
            cur.execute("SELECT DISTINCT loan_date FROM loan_portfolio WHERE loan_date IS NOT NULL ORDER BY loan_date;")
            dates = [row[0] for row in cur.fetchall()]
            print(f"📆 Found {len(dates)} unique loan dates")

            if not banks or not dates:
                print("❌ No banks or loan dates found — aborting.")
                return

            insert_sql = """
                INSERT INTO bank_daily_deposits (bank_id, deposit_date, deposits)
                VALUES (%s, %s, %s)
                ON CONFLICT (bank_id, deposit_date)
                DO UPDATE SET deposits = EXCLUDED.deposits;
            """

            for bank_id, base_deposit in banks:
                # Convert Decimal to float
                base_deposit = float(base_deposit)
                current_deposit = base_deposit

                for dt in dates:
                    drift = random.uniform(-0.005, 0.005)
                    current_deposit *= (1 + drift)
                    current_deposit = max(current_deposit, base_deposit * 0.7)
                    value = round(current_deposit, 2)

                    print(f"→ INSERT: bank_id={bank_id}, date={dt}, deposits={value}")
                    cur.execute(insert_sql, (bank_id, dt, value))

        conn.commit()
        print("✅ Finished inserting all deposit rows.")

if __name__ == "__main__":
    simulate_daily_deposits()
