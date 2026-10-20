-- Cleaned fact table: deduplicated, invalid rows removed, missing product names
-- repaired from the products dimension, cancelled orders excluded from revenue.

CREATE VIEW fact_sales AS
WITH dedup AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY order_item_id ORDER BY order_item_id) AS rn
    FROM order_items
)
SELECT
    d.order_item_id,
    d.order_id,
    o.customer_id,
    o.order_date,
    DATE_TRUNC('month', o.order_date)                  AS sales_month,
    o.channel,
    o.status,
    d.product_id,
    COALESCE(NULLIF(TRIM(d.product_name), ''), p.product_name) AS product_name,
    p.category,
    c.region,
    c.segment,
    d.quantity,
    d.unit_price,
    d.quantity * d.unit_price                          AS revenue
FROM dedup d
JOIN orders    o ON o.order_id    = d.order_id
JOIN products  p ON p.product_id  = d.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE d.rn = 1
  AND d.unit_price > 0
  AND d.quantity  > 0
  AND o.status <> 'Cancelled';
