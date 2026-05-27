from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _empty_grouped_df(primary_col: str) -> pd.DataFrame:
    return pd.DataFrame(columns=[primary_col, "revenue"])


def calculate_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """Calculate KPI bundle from cleaned sales data."""
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_orders": 0,
            "average_order_value": 0.0,
            "total_quantity_sold": 0,
            "monthly_growth_rate": np.nan,
            "revenue_by_month": _empty_grouped_df("month"),
            "revenue_by_category": _empty_grouped_df("category"),
            "top_products": pd.DataFrame(columns=["product_name", "revenue", "quantity"]),
            "top_customers": pd.DataFrame(columns=["customer_name", "revenue", "orders"]),
            "insights": ["No data available after cleaning and filtering."],
        }

    working_df = df.copy()
    working_df["month"] = working_df["order_date"].dt.to_period("M").astype(str)

    total_revenue = float(working_df["revenue"].sum())
    total_orders = int(working_df["order_id"].nunique())
    total_quantity = int(working_df["quantity"].sum())
    avg_order_value = float(total_revenue / total_orders) if total_orders else 0.0

    revenue_by_month = (
        working_df.groupby("month", as_index=False)["revenue"].sum().sort_values("month").reset_index(drop=True)
    )

    monthly_growth_rate = np.nan
    if len(revenue_by_month) >= 2:
        previous_value = float(revenue_by_month.iloc[-2]["revenue"])
        current_value = float(revenue_by_month.iloc[-1]["revenue"])
        if previous_value > 0:
            monthly_growth_rate = (current_value - previous_value) / previous_value

    revenue_by_category = (
        working_df.groupby("category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    )

    top_products = (
        working_df.groupby("product_name", as_index=False)
        .agg(revenue=("revenue", "sum"), quantity=("quantity", "sum"))
        .sort_values("revenue", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )

    top_customers = (
        working_df.groupby("customer_name", as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
        .sort_values("revenue", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )

    kpis: dict[str, Any] = {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "average_order_value": avg_order_value,
        "total_quantity_sold": total_quantity,
        "monthly_growth_rate": monthly_growth_rate,
        "revenue_by_month": revenue_by_month,
        "revenue_by_category": revenue_by_category,
        "top_products": top_products,
        "top_customers": top_customers,
    }
    kpis["insights"] = generate_business_insights(kpis)
    return kpis


def generate_business_insights(kpis: dict[str, Any]) -> list[str]:
    """Generate concise BA-friendly insights based on calculated KPIs."""
    insights: list[str] = []

    total_revenue = float(kpis.get("total_revenue", 0.0))
    total_orders = int(kpis.get("total_orders", 0))
    aov = float(kpis.get("average_order_value", 0.0))
    growth = kpis.get("monthly_growth_rate", np.nan)

    insights.append(
        f"The business generated ${total_revenue:,.2f} from {total_orders:,} unique orders, with an average order value of ${aov:,.2f}."
    )

    if not pd.isna(growth):
        direction = "increased" if growth >= 0 else "decreased"
        insights.append(f"Month-over-month revenue {direction} by {abs(growth) * 100:.2f}% in the latest month.")
    else:
        insights.append("Monthly growth rate is unavailable because there is not enough month-level history.")

    top_products = kpis.get("top_products", pd.DataFrame())
    if not top_products.empty and total_revenue > 0:
        top_product = top_products.iloc[0]
        product_share = float(top_product["revenue"]) / total_revenue
        insights.append(
            f"Top product is {top_product['product_name']} with ${top_product['revenue']:,.2f} revenue ({product_share * 100:.2f}% share)."
        )

    revenue_by_category = kpis.get("revenue_by_category", pd.DataFrame())
    if not revenue_by_category.empty and total_revenue > 0:
        top_category = revenue_by_category.iloc[0]
        category_share = float(top_category["revenue"]) / total_revenue
        insights.append(
            f"Top category is {top_category['category']} contributing ${top_category['revenue']:,.2f} ({category_share * 100:.2f}% of total revenue)."
        )

    top_customers = kpis.get("top_customers", pd.DataFrame())
    if not top_customers.empty and total_revenue > 0:
        top_customer_revenue = float(top_customers["revenue"].sum())
        customer_concentration = top_customer_revenue / total_revenue
        insights.append(
            f"Top 5 customers contribute {customer_concentration * 100:.2f}% of revenue, indicating customer concentration level to monitor."
        )

    return insights
