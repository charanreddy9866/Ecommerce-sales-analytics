-- Raw tables loaded from CSV. Written in ANSI/PostgreSQL-style SQL so it also runs on Redshift.

CREATE TABLE customers (
    customer_id   INTEGER PRIMARY KEY,
    signup_date   DATE,
    region        VARCHAR(20),
    segment       VARCHAR(20)
);

CREATE TABLE products (
    product_id    INTEGER PRIMARY KEY,
    product_name  VARCHAR(100),
    category      VARCHAR(50),
    list_price    DECIMAL(10, 2)
);

CREATE TABLE orders (
    order_id      INTEGER PRIMARY KEY,
    customer_id   INTEGER REFERENCES customers (customer_id),
    order_date    DATE,
    channel       VARCHAR(20),
    status        VARCHAR(20)
);

CREATE TABLE order_items (
    order_item_id INTEGER,            -- not a PK in raw data: duplicates are a known DQ issue
    order_id      INTEGER,
    product_id    INTEGER,
    product_name  VARCHAR(100),
    quantity      INTEGER,
    unit_price    DECIMAL(10, 2)
);
