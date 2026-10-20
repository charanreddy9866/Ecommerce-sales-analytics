-- name: monthly_revenue
-- Monthly revenue, orders, average order value, and month-over-month growth.
WITH monthly AS (
    SELECT
        sales_month,
        SUM(revenue)              AS total_revenue,
        COUNT(DISTINCT order_id)  AS total_orders
    FROM fact_sales
    WHERE status = 'Delivered'
    GROUP BY sales_month
)
SELECT
    sales_month,
    ROUND(total_revenue, 2)                                     AS total_revenue,
    total_orders,
    ROUND(total_revenue / total_orders, 2)                      AS avg_order_value,
    ROUND(100.0 * (total_revenue - LAG(total_revenue) OVER (ORDER BY sales_month))
          / LAG(total_revenue) OVER (ORDER BY sales_month), 1)  AS mom_growth_pct
FROM monthly
ORDER BY sales_month;

-- name: top_products
-- Top 10 products by delivered revenue.
SELECT
    product_name,
    category,
    ROUND(SUM(revenue), 2)    AS revenue,
    SUM(quantity)             AS units_sold
FROM fact_sales
WHERE status = 'Delivered'
GROUP BY product_name, category
ORDER BY revenue DESC
LIMIT 10;

-- name: product_rank_by_month
-- Top 3 products within each month, using a CTE and RANK().
WITH monthly_sales AS (
    SELECT sales_month, product_name, SUM(revenue) AS revenue
    FROM fact_sales
    WHERE status = 'Delivered'
    GROUP BY 1, 2
),
ranked AS (
    SELECT *,
           RANK() OVER (PARTITION BY sales_month ORDER BY revenue DESC) AS product_rank
    FROM monthly_sales
)
SELECT sales_month, product_rank, product_name, ROUND(revenue, 2) AS revenue
FROM ranked
WHERE product_rank <= 3
ORDER BY sales_month, product_rank;

-- name: category_share
-- Revenue share by category, with a running cumulative share (Pareto view).
WITH cat AS (
    SELECT category, SUM(revenue) AS revenue
    FROM fact_sales
    WHERE status = 'Delivered'
    GROUP BY category
)
SELECT
    category,
    ROUND(revenue, 2)                                                      AS revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 1)                       AS pct_of_total,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC)
          / SUM(revenue) OVER (), 1)                                       AS cumulative_pct
FROM cat
ORDER BY revenue DESC;

-- name: return_rate_by_category
-- Return rate by category (returned revenue / gross revenue).
SELECT
    category,
    ROUND(100.0 * SUM(CASE WHEN status = 'Returned' THEN revenue ELSE 0 END)
          / SUM(revenue), 1) AS return_rate_pct
FROM fact_sales
GROUP BY category
ORDER BY return_rate_pct DESC;

-- name: customer_behavior
-- Customer behavior by segment: customers, orders per customer, revenue per customer, repeat rate.
WITH per_customer AS (
    SELECT
        customer_id,
        segment,
        COUNT(DISTINCT order_id) AS orders,
        SUM(revenue)             AS revenue
    FROM fact_sales
    WHERE status = 'Delivered'
    GROUP BY customer_id, segment
)
SELECT
    segment,
    COUNT(*)                                                    AS customers,
    ROUND(AVG(orders), 2)                                       AS orders_per_customer,
    ROUND(AVG(revenue), 2)                                      AS revenue_per_customer,
    ROUND(100.0 * SUM(CASE WHEN orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS repeat_rate_pct
FROM per_customer
GROUP BY segment
ORDER BY revenue_per_customer DESC;

-- name: channel_region
-- Revenue by channel and region.
SELECT
    channel,
    region,
    ROUND(SUM(revenue), 2)    AS revenue,
    COUNT(DISTINCT order_id)  AS orders
FROM fact_sales
WHERE status = 'Delivered'
GROUP BY channel, region
ORDER BY channel, revenue DESC;
