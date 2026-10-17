-- Cloud Services Sales & Profitability Analysis
-- Project 1: PostgreSQL business analysis
-- Dataset: simulated portfolio dataset; results are not actual company performance.
-- First run sql/00_create_table.sql and import data/cloud_saas_sales_clean.csv.
-- Then run these queries against public.cloud_saas_sales_clean.

-- 1. Preview the prepared dataset
SELECT *
FROM public.cloud_saas_sales_clean
LIMIT 10;

-- 2. Overall KPIs
-- Distinct Customer IDs is an ID count, not a verified unique-customer count.
SELECT
    ROUND(SUM("Revenue")::numeric, 2) AS total_revenue,
    ROUND(SUM("Profit")::numeric, 2) AS total_profit,
    ROUND(
        SUM("Profit")::numeric / NULLIF(SUM("Revenue")::numeric, 0) * 100,
        2
    ) AS aggregate_profit_margin_pct,
    COUNT(DISTINCT "Customer_ID") AS distinct_customer_ids,
    COUNT(*) AS analysis_rows
FROM public.cloud_saas_sales_clean;

-- 3. Revenue, profit, and aggregate margin by cloud service
WITH service_summary AS (
    SELECT
        "Cloud_Service",
        COUNT(*) AS transaction_rows,
        SUM("Revenue") AS total_revenue,
        SUM("Profit") AS total_profit
    FROM public.cloud_saas_sales_clean
    GROUP BY "Cloud_Service"
)
SELECT
    "Cloud_Service",
    transaction_rows,
    ROUND(total_revenue::numeric, 2) AS total_revenue,
    ROUND(total_profit::numeric, 2) AS total_profit,
    ROUND(total_profit::numeric / NULLIF(total_revenue::numeric, 0) * 100, 2) AS profit_margin_pct,
    ROUND(total_revenue::numeric / NULLIF(SUM(total_revenue) OVER ()::numeric, 0) * 100, 2) AS revenue_share_pct
FROM service_summary
ORDER BY total_revenue DESC;

-- 4. Revenue, profit, and aggregate margin by customer-segment label
WITH segment_summary AS (
    SELECT
        "Customer_Segment",
        COUNT(*) AS transaction_rows,
        SUM("Revenue") AS total_revenue,
        SUM("Profit") AS total_profit
    FROM public.cloud_saas_sales_clean
    GROUP BY "Customer_Segment"
)
SELECT
    "Customer_Segment",
    transaction_rows,
    ROUND(total_revenue::numeric, 2) AS total_revenue,
    ROUND(total_profit::numeric, 2) AS total_profit,
    ROUND(total_profit::numeric / NULLIF(total_revenue::numeric, 0) * 100, 2) AS profit_margin_pct,
    ROUND(total_revenue::numeric / NULLIF(SUM(total_revenue) OVER ()::numeric, 0) * 100, 2) AS revenue_share_pct
FROM segment_summary
ORDER BY total_revenue DESC;

-- 5. Regional performance (shown as recorded; country-region mappings need QA)
WITH region_summary AS (
    SELECT
        "Region",
        COUNT(*) AS transaction_rows,
        SUM("Revenue") AS total_revenue,
        SUM("Profit") AS total_profit
    FROM public.cloud_saas_sales_clean
    GROUP BY "Region"
)
SELECT
    "Region",
    transaction_rows,
    ROUND(total_revenue::numeric, 2) AS total_revenue,
    ROUND(total_profit::numeric, 2) AS total_profit,
    ROUND(total_profit::numeric / NULLIF(total_revenue::numeric, 0) * 100, 2) AS profit_margin_pct,
    ROUND(total_revenue::numeric / NULLIF(SUM(total_revenue) OVER ()::numeric, 0) * 100, 2) AS revenue_share_pct
FROM region_summary
ORDER BY total_revenue DESC;

-- 6. Revenue, profit, and aggregate margin by country
SELECT
    "Country",
    COUNT(*) AS transaction_rows,
    ROUND(SUM("Revenue")::numeric, 2) AS total_revenue,
    ROUND(SUM("Profit")::numeric, 2) AS total_profit,
    ROUND(
        SUM("Profit")::numeric / NULLIF(SUM("Revenue")::numeric, 0) * 100,
        2
    ) AS profit_margin_pct
FROM public.cloud_saas_sales_clean
GROUP BY "Country"
ORDER BY SUM("Revenue") DESC;

-- 7. Monthly revenue trend (Month should be numeric month 1-12)
SELECT
    "Month" AS month_number,
    ROUND(SUM("Revenue")::numeric, 2) AS total_revenue
FROM public.cloud_saas_sales_clean
GROUP BY "Month"
ORDER BY "Month";

-- 8. Month-over-month revenue growth
WITH monthly_revenue AS (
    SELECT
        "Month" AS month_number,
        SUM("Revenue")::numeric AS total_revenue
    FROM public.cloud_saas_sales_clean
    GROUP BY "Month"
),
monthly_with_previous AS (
    SELECT
        month_number,
        total_revenue,
        LAG(total_revenue) OVER (ORDER BY month_number) AS previous_month_revenue
    FROM monthly_revenue
)
SELECT
    month_number,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(previous_month_revenue, 2) AS previous_month_revenue,
    ROUND(total_revenue - previous_month_revenue, 2) AS revenue_change,
    ROUND(
        (total_revenue - previous_month_revenue)
        / NULLIF(previous_month_revenue, 0) * 100,
        2
    ) AS mom_growth_pct
FROM monthly_with_previous
ORDER BY month_number;

-- 9. Profitability by service and customer-segment label
-- Aggregate margin = sum(Profit) / sum(Revenue), not the mean of row-level margins.
SELECT
    "Customer_Segment",
    "Cloud_Service",
    COUNT(*) AS transaction_rows,
    ROUND(SUM("Revenue")::numeric, 2) AS total_revenue,
    ROUND(SUM("Profit")::numeric, 2) AS total_profit,
    ROUND(
        SUM("Profit")::numeric / NULLIF(SUM("Revenue")::numeric, 0) * 100,
        2
    ) AS profit_margin_pct
FROM public.cloud_saas_sales_clean
GROUP BY "Customer_Segment", "Cloud_Service"
ORDER BY SUM("Revenue") DESC;
