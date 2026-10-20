-- Data-quality checks on the raw order_items table.
-- Each query returns one row: check name and number of failing rows.

-- 1. Exact duplicate line items
SELECT 'duplicate_line_items' AS check_name, COUNT(*) AS failing_rows
FROM (
    SELECT order_item_id, COUNT(*) AS n
    FROM order_items
    GROUP BY order_item_id
    HAVING COUNT(*) > 1
) d;

-- 2. Missing product names
SELECT 'missing_product_name' AS check_name, COUNT(*) AS failing_rows
FROM order_items
WHERE product_name IS NULL OR TRIM(product_name) = '';

-- 3. Invalid prices (zero or negative)
SELECT 'invalid_unit_price' AS check_name, COUNT(*) AS failing_rows
FROM order_items
WHERE unit_price IS NULL OR unit_price <= 0;

-- 4. Invalid quantities
SELECT 'invalid_quantity' AS check_name, COUNT(*) AS failing_rows
FROM order_items
WHERE quantity IS NULL OR quantity <= 0;

-- 5. Orphan line items (no matching order)
SELECT 'orphan_order_items' AS check_name, COUNT(*) AS failing_rows
FROM order_items oi
LEFT JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_id IS NULL;
