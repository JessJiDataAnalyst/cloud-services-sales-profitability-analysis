"""Prepare and analyze the simulated cloud-services sales dataset.

Run from the repository root with:
    python python/cloud_saas_analysis.py

Input:  data/cloud_saas_sales_raw.csv
Outputs:
    data/cloud_saas_sales_clean.csv
    reports/monthly_revenue_trend_python.png

This portfolio dataset is simulated and does not represent an actual company.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
REPORTS_DIR = PROJECT_DIR / "reports"
RAW_FILE = DATA_DIR / "cloud_saas_sales_raw.csv"
CLEAN_FILE = DATA_DIR / "cloud_saas_sales_clean.csv"
CHART_FILE = REPORTS_DIR / "monthly_revenue_trend_python.png"
REQUIRED_COLUMNS = {
    "Date",
    "Customer_ID",
    "Country",
    "Customer_Segment",
    "Cloud_Service",
    "Region",
    "Revenue",
    "Cost",
}


def main() -> None:
    """Load, clean, summarize, and export the analysis dataset."""
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {RAW_FILE}\n"
            "Place cloud_saas_sales_raw.csv in the repository's data/ folder."
        )

    raw_df = pd.read_csv(RAW_FILE)
    original_row_count = len(raw_df)

    # Remove a CSV-export row index if present; it is not an analytical field.
    index_columns = [
        column for column in raw_df.columns
        if str(column).strip().lower().startswith("unnamed:")
    ]
    if index_columns:
        raw_df = raw_df.drop(columns=index_columns)

    missing_columns = REQUIRED_COLUMNS.difference(raw_df.columns)
    if missing_columns:
        raise ValueError(
            "The input CSV is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    duplicate_rows_removed = int(raw_df.duplicated().sum())
    deduplicated_df = raw_df.drop_duplicates().copy()

    # Exclude rows that cannot support revenue/profit calculations.
    missing_financial_mask = deduplicated_df[["Revenue", "Cost"]].isna().any(axis=1)
    missing_financial_rows_removed = int(missing_financial_mask.sum())
    financial_df = deduplicated_df.loc[~missing_financial_mask].copy()

    # Parse dates strictly so invalid values are surfaced rather than silently lost.
    financial_df["Date"] = pd.to_datetime(financial_df["Date"], errors="raise")

    # Standardize category labels used for grouped analysis.
    financial_df["Country"] = (
        financial_df["Country"].astype("string").str.strip().str.title()
    ).replace({"Uae": "UAE"})
    financial_df["Customer_Segment"] = (
        financial_df["Customer_Segment"].astype("string").str.strip().str.title()
    ).replace({"Smb": "SMB"})
    financial_df["Cloud_Service"] = (
        financial_df["Cloud_Service"].astype("string").str.strip()
    )
    financial_df["Region"] = financial_df["Region"].astype("string").str.strip()

    # Create analysis fields used by SQL and the Power BI dashboard.
    # Round row-level profit to cents to keep the exported monetary field tidy.
    financial_df["Profit"] = (financial_df["Revenue"] - financial_df["Cost"]).round(2)
    financial_df["Profit_margin"] = (
        financial_df["Profit"]
        / financial_df["Revenue"].where(financial_df["Revenue"] != 0)
    ) * 100
    financial_df["Month"] = financial_df["Date"].dt.month

    financial_df.to_csv(CLEAN_FILE, index=False)

    total_revenue = financial_df["Revenue"].sum()
    total_profit = financial_df["Profit"].sum()
    aggregate_margin = (
        total_profit / total_revenue * 100 if total_revenue else float("nan")
    )
    distinct_ids = financial_df["Customer_ID"].nunique(dropna=True)

    print("DATA QUALITY SUMMARY")
    print(f"Rows in raw CSV: {original_row_count:,}")
    print(f"Non-analytical index columns removed: {index_columns or 'None detected'}")
    print(f"Exact duplicate rows removed: {duplicate_rows_removed:,}")
    print(f"Rows excluded for missing Revenue or Cost: {missing_financial_rows_removed:,}")
    print(
        f"Prepared rows and columns: {financial_df.shape[0]:,} rows × "
        f"{financial_df.shape[1]} columns"
    )
    print(f"Prepared file saved to: {CLEAN_FILE}")

    print("\nOVERALL KPIs")
    print(f"Total revenue: {total_revenue:,.2f}")
    print(f"Total profit: {total_profit:,.2f}")
    print(f"Aggregate profit margin: {aggregate_margin:.2f}%")
    print(
        "Distinct Customer IDs (not a verified unique-customer count): "
        f"{distinct_ids:,}"
    )

    service_summary = financial_df.groupby("Cloud_Service", dropna=False).agg(
        transaction_rows=("Revenue", "size"),
        revenue=("Revenue", "sum"),
        profit=("Profit", "sum"),
    )
    service_summary["profit_margin_pct"] = (
        service_summary["profit"]
        / service_summary["revenue"].replace(0, pd.NA)
        * 100
    )
    service_summary = service_summary.sort_values("revenue", ascending=False)
    print("\nREVENUE, PROFIT, AND MARGIN BY SERVICE")
    print(service_summary.round(2).to_string())

    segment_summary = financial_df.groupby("Customer_Segment", dropna=False).agg(
        transaction_rows=("Revenue", "size"),
        revenue=("Revenue", "sum"),
        profit=("Profit", "sum"),
    )
    segment_summary["profit_margin_pct"] = (
        segment_summary["profit"]
        / segment_summary["revenue"].replace(0, pd.NA)
        * 100
    )
    segment_summary = segment_summary.sort_values("revenue", ascending=False)
    print("\nREVENUE, PROFIT, AND MARGIN BY SEGMENT LABEL")
    print(segment_summary.round(2).to_string())

    monthly_revenue = (
        financial_df.groupby("Month")["Revenue"]
        .sum()
        .reindex(range(1, 13), fill_value=0)
    )
    monthly_summary = pd.DataFrame(
        {
            "revenue": monthly_revenue,
            "mom_growth_pct": monthly_revenue.pct_change() * 100,
        }
    )
    print("\nMONTHLY REVENUE AND MONTH-OVER-MONTH CHANGE")
    print(monthly_summary.round(2).to_string())

    # Save a reproducible chart in the reports/ directory.
    month_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly_revenue.index, monthly_revenue.values, marker="o")
    ax.set_title("Monthly Revenue Trend (2025)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (dataset units)")
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda value, _position: f"{value / 1_000_000:.1f}M")
    )
    ax.set_xticks(range(1, 13), month_labels)
    ax.set_ylim(bottom=0)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(CHART_FILE, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"\nMonthly revenue chart saved to: {CHART_FILE}")
    print(
        "\nNote: This script does not automatically correct the nine country–region "
        "mapping discrepancies identified during QA. Review README.md before "
        "interpreting regional results."
    )


if __name__ == "__main__":
    main()
