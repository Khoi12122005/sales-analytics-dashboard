import pandas as pd

from src.kpi_calculator import calculate_kpis


def test_calculate_kpis_returns_expected_values():
    df = pd.DataFrame(
        {
            "order_id": ["O1", "O2", "O3", "O4"],
            "order_date": pd.to_datetime(["2026-01-10", "2026-01-20", "2026-02-05", "2026-02-22"]),
            "customer_name": ["Alice", "Bob", "Alice", "David"],
            "product_name": ["Laptop", "Mouse", "Laptop", "Keyboard"],
            "category": ["Electronics", "Accessories", "Electronics", "Accessories"],
            "quantity": [1, 2, 1, 3],
            "unit_price": [1000, 20, 1000, 50],
            "revenue": [1000, 40, 1000, 150],
        }
    )

    kpis = calculate_kpis(df)

    assert kpis["total_revenue"] == 2190
    assert kpis["total_orders"] == 4
    assert kpis["total_quantity_sold"] == 7
    assert kpis["average_order_value"] == 547.5

    revenue_by_month = kpis["revenue_by_month"]
    jan = float(revenue_by_month.loc[revenue_by_month["month"] == "2026-01", "revenue"].iloc[0])
    feb = float(revenue_by_month.loc[revenue_by_month["month"] == "2026-02", "revenue"].iloc[0])
    assert jan == 1040
    assert feb == 1150
    assert round(kpis["monthly_growth_rate"], 6) == round((1150 - 1040) / 1040, 6)

    assert len(kpis["top_products"]) <= 5
    assert len(kpis["top_customers"]) <= 5
    assert len(kpis["insights"]) >= 3
