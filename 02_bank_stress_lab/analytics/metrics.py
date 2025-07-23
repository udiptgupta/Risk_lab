# LDR, NPL%, CAR

from datetime import date
from analytics.db import get_conn

AS_OF = date(2025, 7, 23) #change daily
def compute_base_metrics(as_of = AS_OF):
    sql = """
        SELECT b.bank_id, b.total_deposits, b.capital,
            SUM(l.current_bal) AS total_loans,
            SUM(l.current_bal * l.risk_weight) AS risk_weighted_loans,
            SUM(l.current_bal) FILTER (WHERE l.default_flag) AS npl_amt
        FROM banks b
        LEFT JOIN loan_portfolio l ON b.bank_id = l.bank_id
        GROUP BY b.bank_id, b.total_deposits, b.capital
        ORDER by b.bank_id;
    """

    insert_sql = """
        INSERT INTO bank_metrics (as_of, bank_id, loans_amt, deposits_amt, npl_amt, ldr, npl_pct, car)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (as_of, bank_id)
        DO UPDATE SET loans_amt = EXCLUDED.loans_amt,
                        deposits_amt = EXCLUDED.deposits_amt,
                        npl_amt = EXCLUDED.npl_amt,
                        ldr = EXCLUDED.ldr,
                        npl_pct = EXCLUDED.npl_pct,
                        car = EXCLUDED.car;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

            for bank_id, deposits, capital, total_loans, risk_weighted_loans, npl_amt in rows:
                if not total_loans or total_loans == 0:
                    ldr = None
                    npl_pct = None
                    car = None
                else:
                    ldr = total_loans / deposits if deposits else None
                    npl_pct = npl_amt / total_loans if npl_amt else 0
                    car = capital / risk_weighted_loans if risk_weighted_loans else None
        
                cur.execute(insert_sql, (as_of ,bank_id, total_loans, deposits, npl_amt, ldr, npl_pct, car))
        conn.commit()

if __name__ == "__main__":
    compute_base_metrics()
