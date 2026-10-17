-- Cloud Services Sales & Profitability Analysis
-- Create the destination table before importing data/cloud_saas_sales_clean.csv.
-- The dataset is simulated portfolio practice data, not actual company data.

CREATE TABLE IF NOT EXISTS public.cloud_saas_sales_clean (
    "Date" DATE NOT NULL,
    "Customer_ID" TEXT,
    "Country" TEXT,
    "Customer_Segment" TEXT,
    "Cloud_Service" TEXT,
    "Region" TEXT,
    "Revenue" NUMERIC(14, 2) NOT NULL,
    "Cost" NUMERIC(14, 2) NOT NULL,
    "Profit" NUMERIC(14, 2) NOT NULL,
    "Profit_margin" NUMERIC(10, 6),
    "Month" SMALLINT CHECK ("Month" BETWEEN 1 AND 12)
);

-- Load the prepared CSV into this table using DBeaver's Import Data feature,
-- or run the following psql command from the repository root after confirming
-- the table is empty (do not import twice):
-- \copy public.cloud_saas_sales_clean FROM 'data/cloud_saas_sales_clean.csv' WITH (FORMAT csv, HEADER true);
