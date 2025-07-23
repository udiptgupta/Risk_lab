#daily progress
# Bank Stress Lab – Build Log

*Project*: **Bank Stress Dashboard (Tableau Edition)**
*Path*: `D:/09_Risk_lab/02_bank_stress_lab/`
*Timezone*: Asia/Kolkata (IST, UTC+05:30)

This log tracks day-by-day build progress. Short, factual, execution-oriented.

---

## Day 0 – Project Skeleton + Environment Setup

**Date:** July 21, 2025 (IST)
**Goal:** Create the working structure, environment, and DB connectivity foundation.

### Done

* Created base project folder: `bank_stress_lab/` (actually under `D:/09_Risk_lab/02_bank_stress_lab/`).
* Added subfolders: `analytics/`, `db/`, `data/raw`, `data/processed`, `tableau_exports/`, `notebooks/`, `tests/`.
* Created initial project files (placeholders):

  * `.env` (DB creds)
  * `requirements.txt`
  * `README.md` (stub)
  * `build_log.md` (this log)
* Created/activated Python env (`risklab_env`).
* Installed core packages: `psycopg2-binary`, `python-dotenv`, `pandas`, `numpy`.
* Wrote **`analytics/db.py`**:

  * Loads env vars.
  * Connects to PostgreSQL via `psycopg2`.
  * Test query: `SELECT COUNT(*) FROM banks;`.
* Fixed `.env` key mismatch (`DB_PASS` → `DB_PASSWORD`).
* Verified successful DB connection from Python.

### Git

Initial repo created & first commit: **"Day 0 – project skeleton + DB connection test"**.

---

## Day 1 – DB Schema + Banks + Synthetic Loan Generator

**Date:** July 22, 2025 (IST)
**Focused Work Window:** \~15:20–17:30 IST (2h+ stretch; 40m overtime for Python).

### Database Work

Connected to PostgreSQL (`psql -U postgres -h localhost`).

**Created DB:**

```sql
CREATE DATABASE bank_stress_db;
\c bank_stress_db;
```

**Created tables:**

* `banks`
* `loan_portfolio`

Both verified using `\dt` and `\d <table>`.

**Inserted 5 sample banks:**

```sql
INSERT INTO banks (bank_name, capital, total_loans, total_deposits) VALUES
('METROPOLITAN',    2857000230.45, 237245600,   3452200000),
('RIVERBANK',      56000000000,    8596210000,  5665578994),
('SUNRISE FINANCE',   56500000,       85910000,   905008994),
('IRON TRUST',       300002500,     2500000000, 10000000000),
('CRESCENT BANK',    200002500,     2500000000,  8000000000);
```

**Quick Ratio Check – LDR:**

```sql
SELECT bank_name, ROUND(total_loans / total_deposits, 4) AS ldr
FROM banks;
```

*Output Highlights:* RIVERBANK > 1.5 (loan heavy), METROPOLITAN & SUNRISE deposit-rich (<0.10).

### Manual Seed Loans (pre‑script sanity)

Inserted a handful of rows into `loan_portfolio` for banks 1–3 to validate schema, booleans, and aggregation logic.

Validated:

```sql
SELECT bank_id,
       SUM(current_bal) AS total_loans,
       SUM(current_bal) FILTER (WHERE default_flag) AS npl_loans,
       ROUND(SUM(current_bal) FILTER (WHERE default_flag) * 100.0 / SUM(current_bal), 2) AS npl_pct
FROM loan_portfolio
GROUP BY bank_id;
```

Confirmed NPL% math behaves as expected: Bank 3 \~96%, Bank 2 \~45%, Bank 1 \~1%.

---

### Python Loan Generator (`analytics/data_generator.py`)

**Purpose:** Seed synthetic loan data across all banks for testing metrics and Tableau later.

#### Functions

**`fetch_banks()`** – Pulls `(bank_id, bank_name)` from `banks` table.
**Bug caught:** Used `with get_conn as conn:` instead of `with get_conn() as conn:`. Fixed.

**`generate_loans_for_bank(bank_id, n_loans=10, default_prob=0.05)`**

* Random orig amount: 10k–5M.
* Current balance: 50%–100% of orig (simulate amortization).
* Default probability \~5% (Bernoulli).
* Risk weight: 1.0 if default, else 0.5.
* Segment random from: Retail, Corporate, SME, Agri, Mortgage.
* Returns list of tuples: `(bank_id, orig_amt, current_bal, default_flag, risk_weight, seg_code)`.

**`bulk_insert_loans(rows)`**

* Uses `psycopg2.extras.execute_values` for fast bulk insert.
* SQL stub with `VALUES %s` placeholder.
* Single commit after batch insert.

#### Run

Executed via:

```bash
python -m analytics.data_generator
```

Inserted **10 synthetic loans per bank** (total new = 50). Combined with manual seeds → totals per bank now show 10–13 loans each.

#### Validation Query Post‑Insert

```sql
SELECT bank_id, COUNT(*) AS loan_ct,
       SUM(current_bal) AS loan_amt,
       SUM(current_bal) FILTER (WHERE default_flag) AS npl_amt
FROM loan_portfolio
GROUP BY bank_id
ORDER BY bank_id;
```

*Results (rounded):*

* Bank 1: 13 loans | \~168.6M | NPL \~2.1M
* Bank 2: 12 loans | \~20.0M  | NPL \~5.0M
* Bank 3: 12 loans | \~25.1M  | NPL \~5.0M
* Bank 4: 10 loans | \~21.2M  | NPL \~0
* Bank 5: 10 loans | \~13.3M  | NPL \~0

All good.

---

### Issues Caught & Fixed (Day 1)

| Issue                                          | Cause                                             | Fix                               | Status   |
| ---------------------------------------------- | ------------------------------------------------- | --------------------------------- | -------- |
| "no password supplied"                         | `.env` var misnamed (`DB_PASS`)                   | Renamed to `DB_PASSWORD` + re-run | Resolved |
| TypeError: function object not context manager | Used `with get_conn` instead of `with get_conn()` | Added parentheses                 | Resolved |
| Syntax error typing `SELECT`                   | Trailing comma + stray `/dt`                      | Corrected syntax                  | Resolved |

---

## Git – Day 1 Commit

After validating inserts & script run:

```bash
git add .
git commit -m "Day 1 – DB schema, sample banks inserted, data_generator script"
```

(If large DB creds present, confirm `.gitignore` excludes `.env`.)

---

## Next Up – Day 2 Plan (Preview)

**Target Date:** July 23, 2025 (IST)
**Time Block:** 2 hrs.

Tasks:

1. Build `analytics/metrics.py`.
2. Aggregate `loan_portfolio` → per-bank totals + NPL + RWA.
3. Join to `banks` (capital, deposits) → compute LDR, NPL%, CAR.
4. Insert into `bank_metrics` table (`as_of` date param).
5. Validate with SQL cross-check queries.

Stretch: Update `banks.total_loans` to match portfolio sums (optional — or leave raw to show modeling adjustments).

---

## Running Totals / Progress Snapshot

* **DB Ready:** ✅
* **Banks Seeded:** 5
* **Loans Seeded:** 57 total (manual + generated) – scaling tomorrow.
* **Python DB Connect:** ✅
* **Loan Generator:** ✅ (parameterized, reproducible via seed)
* **Metrics Pipeline:** Pending (Day 2)

---

# Day 2 – Bank Stress Dashboard Build Log

## Key Progress
- Implemented `compute_base_metrics()` to calculate:
  - **LDR (Loan-to-Deposit Ratio)**
  - **NPL% (Non-Performing Loan Percentage)**
  - **CAR (Capital Adequacy Ratio)** using risk-weighted loans.
- Fixed SQL and Python bugs (e.g., tuple unpacking, column mapping).
- Expanded dataset to **2,500+ loans** via `data_generator.py` for realistic metrics.
- Executed advanced SQL queries:
  - Corporate exposure percentage by bank.
  - Segment-wise loan totals.
- Verified metrics storage in `bank_metrics` table with updated CAR values.

## Current Metrics Snapshot
- **RIVERBANK** leads with CAR ~115%.
- Data now reflects a more realistic LDR and NPL distribution.

## Next Steps (Day 3)
- Automate daily metric computation.
- Add trend analysis (time-series metrics).
- Start planning Tableau dashboard integration.

