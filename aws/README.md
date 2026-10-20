# AWS extension: S3 + Redshift Serverless

Status: **planned, not yet run.** Complete these steps in your own AWS account before listing S3 or Redshift as done.

## Steps

1. **Create an S3 bucket** (for example `ecommerce-sales-analytics-<yourname>`) and upload the four CSVs:
   ```bash
   aws s3 cp data/ s3://<bucket>/raw/ --recursive --exclude "*" --include "*.csv"
   ```
2. **Create a Redshift Serverless workgroup** (the free trial covers this project) and an IAM role that lets Redshift read the bucket.
3. **Create the tables** by running `sql/01_schema.sql` in the Redshift query editor.
4. **Load the data** by running `aws/redshift_load.sql` after filling in the bucket name and IAM role ARN.
5. **Run the model and analysis** with `sql/02_data_quality.sql`, `sql/03_clean_model.sql` and `sql/04_analysis.sql`. They are written in PostgreSQL-style SQL that Redshift supports.
6. **Point Power BI at Redshift** using the built-in Amazon Redshift connector, replacing the CSV sources.
7. **Delete the workgroup and bucket** when you're done, so you aren't billed after the trial.
