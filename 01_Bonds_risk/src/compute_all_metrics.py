# src/compute_all_metrics.py
from datetime import date
from src.utils.db import get_conn
from src.bond_analytics import price_and_duration

AS_OF_DATE = date(2025, 7, 20)  # you can change this dynamically if needed

def compute_and_store_metrics(as_of=AS_OF_DATE):
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Fetch all bond IDs
            cur.execute("SELECT bond_id FROM bonds;")
            bond_ids = [row[0] for row in cur.fetchall()]

            # Insert metrics
            for bond_id in bond_ids:
                try:
                    metrics = price_and_duration(bond_id, as_of)
                    cur.execute("""
                        INSERT INTO bond_risk_metrics
                        (bond_id, as_of, price, macaulay_duration, modified_duration, convexity)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (bond_id, as_of)
                        DO UPDATE SET
                            price = EXCLUDED.price,
                            macaulay_duration = EXCLUDED.macaulay_duration,
                            modified_duration = EXCLUDED.modified_duration,
                            convexity = EXCLUDED.convexity;
                    """, (
                        bond_id, as_of,
                        metrics['price'],
                        metrics['macaulay_duration'],
                        metrics['modified_duration'],
                        metrics['convexity']
                    ))
                except Exception as e:
                    print(f"Error processing bond {bond_id}: {e}")
            conn.commit()

if __name__ == "__main__":
    compute_and_store_metrics()
    print(f"Metrics computed and stored for {AS_OF_DATE}.")
