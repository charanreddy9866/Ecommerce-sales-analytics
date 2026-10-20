"""Build dashboard/index.html from the CSVs in reports/.

Reads the analysis outputs, computes the headline KPIs, and injects everything
as JSON into dashboard/template.html. Run after scripts/run_pipeline.py.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS, DASH = ROOT / "reports", ROOT / "dashboard"


def read(name):
    with open(REPORTS / f"{name}.csv") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            if v == "":
                r[k] = None
                continue
            try:
                r[k] = float(v) if any(c in v for c in ".e") else int(v)
            except ValueError:
                pass
    return rows


monthly = read("monthly_revenue")
for m in monthly:
    m["sales_month"] = str(m["sales_month"])[:10]
segments = read("customer_behavior")

by_year = {}
for m in monthly:
    by_year[m["sales_month"][:4]] = by_year.get(m["sales_month"][:4], 0) + m["total_revenue"]
revenue = sum(m["total_revenue"] for m in monthly)
orders = sum(m["total_orders"] for m in monthly)
peak = max(monthly, key=lambda m: m["total_revenue"])

dq_labels = {
    "duplicate_line_items": ("Duplicate line items", "removed"),
    "missing_product_name": ("Missing product names", "repaired"),
    "invalid_unit_price": ("Zero or negative prices", "removed"),
    "invalid_quantity": ("Zero quantities", "removed"),
    "orphan_order_items": ("Line items with no matching order", "removed"),
}

data = {
    "kpis": {
        "revenue": revenue,
        "orders": orders,
        "aov": revenue / orders,
        "yoy_pct": (by_year["2025"] / by_year["2024"] - 1) * 100,
        "repeat_rate": sum(s["customers"] * s["repeat_rate_pct"] for s in segments) / sum(s["customers"] for s in segments),
        "peak_month": peak["sales_month"],
        "peak_revenue": peak["total_revenue"],
    },
    "monthly": monthly,
    "products": read("top_products"),
    "categories": read("category_share"),
    "segments": segments,
    "leaders": [{**r, "sales_month": str(r["sales_month"])[:10]} for r in read("product_rank_by_month")],
    "channels": read("channel_region"),
    "returns": read("return_rate_by_category"),
    "dq": [{"label": dq_labels[r["check_name"]][0], "action": dq_labels[r["check_name"]][1], "failing_rows": r["failing_rows"]}
           for r in read("data_quality_report")],
}

body = (DASH / "template.html").read_text().replace("__DATA__", json.dumps(data))
html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n</head>\n<body>\n'
        + body + '\n</body>\n</html>\n')
(DASH / "index.html").write_text(html)
print(f"wrote {DASH / 'index.html'} ({len(html) / 1024:.0f} KB)")
