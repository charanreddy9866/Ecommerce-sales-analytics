"""Load the CSVs into DuckDB, run data-quality checks, build the clean model,
run the analysis queries, and export results for Power BI plus summary charts.

Usage: python scripts/run_pipeline.py
"""
import re
from pathlib import Path

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA, SQL, REPORTS = ROOT / "data", ROOT / "sql", ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

con = duckdb.connect()

# 1. Schema + load
con.execute((SQL / "01_schema.sql").read_text())
for t in ["customers", "products", "orders", "order_items"]:
    con.execute(f"INSERT INTO {t} SELECT * FROM read_csv_auto('{DATA / (t + '.csv')}', header=true)")
    print(f"loaded {t}: {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:,} rows")

# 2. Data-quality checks
print("\nData-quality checks")
dq_rows = []
for stmt in [s for s in (SQL / "02_data_quality.sql").read_text().split(";") if "SELECT" in s]:
    name, n = con.execute(stmt).fetchone()
    dq_rows.append((name, n))
    print(f"  {name:<24} {n:>5} {'FAIL' if n else 'PASS'}")
with open(REPORTS / "data_quality_report.csv", "w") as f:
    f.write("check_name,failing_rows\n")
    f.writelines(f"{n},{c}\n" for n, c in dq_rows)

# 3. Clean model
con.execute((SQL / "03_clean_model.sql").read_text())
raw = con.execute("SELECT COUNT(*) FROM order_items").fetchone()[0]
clean = con.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
print(f"\nfact_sales: {clean:,} clean rows from {raw:,} raw line items")

# 4. Analysis queries -> CSVs (Power BI data sources)
results = {}
for block in re.split(r"^-- name: ", (SQL / "04_analysis.sql").read_text(), flags=re.M)[1:]:
    name, query = block.split("\n", 1)
    df = con.execute(query.strip().rstrip(";")).df()
    df.to_csv(REPORTS / f"{name.strip()}.csv", index=False)
    results[name.strip()] = df
    print(f"  exported {name.strip()}.csv ({len(df)} rows)")

con.execute(f"COPY fact_sales TO '{REPORTS / 'fact_sales.csv'}' (HEADER)")

# 5. Charts
m = results["monthly_revenue"]
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(m["sales_month"], m["total_revenue"] / 1e3, marker="o", color="#1f6feb")
ax.set_title("Monthly delivered revenue ($K)")
ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(REPORTS / "monthly_revenue.png", dpi=120)

tp = results["top_products"].iloc[::-1]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh(tp["product_name"], tp["revenue"] / 1e3, color="#1f6feb")
ax.set_title("Top 10 products by revenue ($K)")
fig.tight_layout(); fig.savefig(REPORTS / "top_products.png", dpi=120)

print("\nDone. Results in reports/")
