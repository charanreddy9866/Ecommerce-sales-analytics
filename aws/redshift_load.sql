-- Load the raw CSVs from S3 into Redshift. Replace <bucket> and <iam-role-arn> first.

COPY customers   FROM 's3://<bucket>/raw/customers.csv'   IAM_ROLE '<iam-role-arn>' CSV IGNOREHEADER 1 DATEFORMAT 'auto';
COPY products    FROM 's3://<bucket>/raw/products.csv'    IAM_ROLE '<iam-role-arn>' CSV IGNOREHEADER 1;
COPY orders      FROM 's3://<bucket>/raw/orders.csv'      IAM_ROLE '<iam-role-arn>' CSV IGNOREHEADER 1 DATEFORMAT 'auto';
COPY order_items FROM 's3://<bucket>/raw/order_items.csv' IAM_ROLE '<iam-role-arn>' CSV IGNOREHEADER 1 EMPTYASNULL;

-- Quick row-count check after loading
SELECT 'customers' AS table_name, COUNT(*) FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items;
