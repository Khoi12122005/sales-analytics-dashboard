import pandas as pd

from src.data_cleaning import clean_sales_data


def test_clean_sales_data_standardizes_and_recalculates_revenue():
    raw_df = pd.DataFrame(
        {
            "order_id": ["A-001", "A-002", "A-002", "A-003"],
            "order_date": ["2026-01-01", "2026-01-03", "2026-01-03", "invalid-date"],
            "customer": ["Alice", "Bob", "Bob", "Charlie"],
            "product": ["Laptop", "Mouse", "Mouse", "Keyboard"],
            "category": ["Electronics", "Accessories", "Accessories", "Accessories"],
            "quantity": ["2", "3", "3", "1"],
            "unit_price": ["1000", "25", "25", "20"],
            "revenue": ["1500", None, "75", "20"],
        }
    )

    cleaned_df, quality_log = clean_sales_data(raw_df)

    assert len(cleaned_df) == 2
    assert quality_log["invalid_date_rows_removed"] == 1
    assert quality_log["duplicate_rows_removed"] == 1

    expected_columns = {
        "order_id",
        "order_date",
        "customer_name",
        "product_name",
        "category",
        "quantity",
        "unit_price",
        "revenue",
    }
    assert expected_columns.issubset(set(cleaned_df.columns))

    assert pd.api.types.is_datetime64_any_dtype(cleaned_df["order_date"])
    assert (cleaned_df["revenue"] == (cleaned_df["quantity"] * cleaned_df["unit_price"]).round(2)).all()


def test_clean_sales_data_handles_missing_order_id_and_negative_values():
    raw_df = pd.DataFrame(
        {
            "order_date": ["2026-02-01", "2026-02-02"],
            "customer_name": ["", "Diana"],
            "product_name": ["Headphone", "Speaker"],
            "category": [None, "Audio"],
            "quantity": ["-2", None],
            "unit_price": ["-99", "120"],
            "revenue": [None, "240"],
        }
    )

    cleaned_df, quality_log = clean_sales_data(raw_df)

    assert len(cleaned_df) == 2
    assert quality_log["generated_order_ids"] == 2
    assert (cleaned_df["quantity"] >= 1).all()
    assert (cleaned_df["unit_price"] >= 0).all()
    assert (cleaned_df["customer_name"] != "").all()
    assert (cleaned_df["category"] != "").all()
