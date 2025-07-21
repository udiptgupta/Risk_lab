\# Build Log



---



\## Day 1 – July 17, 2025

\*\*Focus:\*\* Infrastructure foundation.

\- ✅ Installed \& verified PostgreSQL; created `risklab` DB.

\- ✅ Created table `stg\_bank\_metrics`; loaded seed data; test query (loan-to-deposit ratio) ran.

\- ✅ Created GitHub repo \*\*Risk\_lab\*\*; built structured folders:

&nbsp; `01\_data\_raw/`, `02\_data\_clean/`, `03\_sql/`, `04\_notebooks/`, `05\_excel/`, `06\_dashboards/`, `07\_docs/`.

\- ✅ Added `README.md`, `build\_log.md`.

\- ✅ Linked local project to GitHub; resolved remote/merge errors.

\- ✅ Added `.gitignore` (ignores `envs/`, checkpoints, temp/big files).

\- ✅ Created \& validated `risklab\_env` (Python 3.11) on D:; Jupyter working.



\*\*Elapsed:\*\* ~5 hrs (includes Git + env troubleshooting).



---



\## Day 2 – July 18, 2025

\*\*Focus:\*\* Stabilize Python/Conda stack.

\- ✅ Repaired broken Conda/Anaconda after interrupted update.

\- ✅ Successfully upgraded Conda to latest (v25.x) in base.

\- ✅ Confirmed Anaconda install clean; base Python 3.13 (general), `risklab\_env` Python 3.11 (project).

\- ✅ Verified Jupyter kernels for both envs appear + launch.

\- ✅ Taskbar launch shortcuts created: Base + RiskLab (opens in correct paths).

\- ✅ Uploaded environment/conda cheat sheet to Notion.

\- ✅ Repo intact after updates (no lost packages).



\*\*Elapsed:\*\* ~4 hrs (heavy troubleshooting but now stable).



---
## Day 3 – July 19, 2025

**Focus:** Setup Synthetic Bond Risk Lab data pipeline.

- ✅ Setup project structure for Synthetic Bond Risk Lab.
- ✅ Configured PostgreSQL database `bondrisk_db` and created `bonds` table.
- ✅ Implemented Python <-> PostgreSQL connection using psycopg2.
- ✅ Developed `bond_generator.py` to create 1000 synthetic bonds with realistic attributes.
- ✅ Verified bulk insert of bonds into database (1002 total entries).
- ✅ Repo now has working data pipeline: Python → PostgreSQL.

**Elapsed:** ~2.5 hrs (project structure + data pipeline).

**Next:** Begin risk analytics (duration, convexity) on synthetic bond portfolio.

---

### Day 4 (July 20, 2025)
**Focus:** Yield curves, credit spreads, pricing, and duration analytics.

- Added `yield_curve` and `credit_spread` tables (with synthetic data).
- Implemented `pricing.py` and `bond_analytics.py` to compute price, Macaulay duration, modified duration, and convexity.
- Built `compute_all_metrics.py` to batch-calculate analytics for all bonds.
- Created initial Streamlit dashboard (`app.py`) with table + issuer filters + yield curve plot.
- Fixed Decimal vs float bugs; validated pricing engine.
**Next:** Add interactive bond analytics panel and portfolio-level views.

