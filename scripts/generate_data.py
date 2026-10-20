"""Generate a synthetic e-commerce dataset (customers, products, orders, order_items).

The data is fake but realistic: seasonality, repeat customers, category price
ranges, and a small number of deliberately bad rows (duplicates, missing product
names, invalid prices) so the data-quality checks have something to catch.

Usage: python scripts/generate_data.py  -> writes CSVs to data/
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

N_CUSTOMERS = 12_000
N_ORDERS = 25_000
START, END = date(2024, 1, 1), date(2025, 12, 31)

REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
CHANNELS = ["Web", "Mobile App", "Marketplace"]
CATEGORIES = {
    "Electronics": (40, 900),
    "Home & Kitchen": (10, 250),
    "Apparel": (8, 120),
    "Beauty": (5, 80),
    "Sports & Outdoors": (12, 300),
    "Books": (5, 45),
}

# Customers
customers = []
for cid in range(1, N_CUSTOMERS + 1):
    signup = START + timedelta(days=random.randint(0, 600))
    customers.append({
        "customer_id": cid,
        "signup_date": signup.isoformat(),
        "region": random.choice(REGIONS),
        "segment": random.choices(["Consumer", "Small Business", "Prime"], [0.55, 0.15, 0.30])[0],
    })

# Products
products = []
pid = 1
for cat, (lo, hi) in CATEGORIES.items():
    for i in range(1, 21):
        products.append({
            "product_id": pid,
            "product_name": f"{cat.split()[0]} Item {i:02d}",
            "category": cat,
            "list_price": round(random.uniform(lo, hi), 2),
        })
        pid += 1

# Orders: seasonality (Nov/Dec peak), weighted toward repeat customers
month_weight = {1: .8, 2: .75, 3: .85, 4: .85, 5: .9, 6: .95, 7: 1.1, 8: .95, 9: .9, 10: 1.0, 11: 1.5, 12: 1.7}
days = [START + timedelta(days=d) for d in range((END - START).days + 1)]
day_w = [month_weight[d.month] * (1.08 if d.year == 2025 else 1.0) for d in days]
cust_w = [random.paretovariate(1.2) for _ in customers]
prod_w = [random.paretovariate(2.5) for _ in products]

orders, items = [], []
item_id = 1
for oid in range(1, N_ORDERS + 1):
    c = random.choices(customers, cust_w)[0]
    od = random.choices(days, day_w)[0]
    orders.append({
        "order_id": oid,
        "customer_id": c["customer_id"],
        "order_date": od.isoformat(),
        "channel": random.choices(CHANNELS, [0.5, 0.35, 0.15])[0],
        "status": random.choices(["Delivered", "Returned", "Cancelled"], [0.9, 0.06, 0.04])[0],
    })
    for p in random.choices(products, prod_w, k=random.choices([1, 2, 3, 4], [0.55, 0.25, 0.12, 0.08])[0]):
        discount = random.choice([0, 0, 0, 0.05, 0.10, 0.20])
        items.append({
            "order_item_id": item_id,
            "order_id": oid,
            "product_id": p["product_id"],
            "product_name": p["product_name"],
            "quantity": random.choices([1, 2, 3, 5], [0.7, 0.2, 0.07, 0.03])[0],
            "unit_price": round(p["list_price"] * (1 - discount), 2),
        })
        item_id += 1

# Inject data-quality problems (~0.5% of rows)
for _ in range(60):   # exact duplicate line items
    items.append(dict(random.choice(items)))
for it in random.sample(items, 40):   # missing product names
    it["product_name"] = ""
for it in random.sample(items, 30):   # invalid prices
    it["unit_price"] = random.choice([0, -1 * it["unit_price"]])
for it in random.sample(items, 15):   # invalid quantities
    it["quantity"] = 0

def write(name, rows):
    with open(OUT / f"{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"{name}: {len(rows):,} rows")

write("customers", customers)
write("products", products)
write("orders", orders)
write("order_items", items)
