from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.data_loader import CANONICAL_COLUMNS


def _to_numeric(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace(" ", "", regex=False)
        .replace({"nan": np.nan, "None": np.nan, "": np.nan})
    )
    return pd.to_numeric(cleaned, errors="coerce")


def clean_sales_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean sales dataset and return (cleaned_df, quality_log)."""
    working_df = df.copy()
    quality_log: dict[str, Any] = {
        "rows_initial": int(len(working_df)),
        "rows_final": 0,
        "invalid_date_rows_removed": 0,
        "duplicate_rows_removed": 0,
        "generated_order_ids": 0,
        "revenue_recalculated_rows": 0,
        "missing_columns_added": [],
        "missing_values_filled": {},
        "notes": [],
    }

    for col in CANONICAL_COLUMNS:
        if col not in working_df.columns:
            working_df[col] = np.nan
            quality_log["missing_columns_added"].append(col)

    if working_df["order_id"].isna().all():
        working_df["order_id"] = [f"AUTO-{idx:06d}" for idx in range(1, len(working_df) + 1)]
        quality_log["generated_order_ids"] = int(len(working_df))
        quality_log["notes"].append("order_id was missing from source; generated AUTO IDs.")
    else:
        missing_ids = working_df["order_id"].isna() | (working_df["order_id"].astype(str).str.strip() == "")
        missing_count = int(missing_ids.sum())
        if missing_count > 0:
            auto_ids = [f"AUTO-{idx:06d}" for idx in range(1, missing_count + 1)]
            working_df.loc[missing_ids, "order_id"] = auto_ids
            quality_log["generated_order_ids"] = missing_count
    working_df["order_id"] = working_df["order_id"].astype(str).str.strip()

    working_df["order_date"] = pd.to_datetime(working_df["order_date"], errors="coerce", dayfirst=False)
    invalid_date_mask = working_df["order_date"].isna()
    quality_log["invalid_date_rows_removed"] = int(invalid_date_mask.sum())
    working_df = working_df.loc[~invalid_date_mask].copy()

    for text_col in ["customer_name", "product_name", "category"]:
        before_missing = int(working_df[text_col].isna().sum() + (working_df[text_col].astype(str).str.strip() == "").sum())
        working_df[text_col] = (
            working_df[text_col]
            .astype(str)
            .replace({"nan": np.nan, "None": np.nan})
            .str.strip()
        )
        working_df[text_col] = working_df[text_col].replace("", np.nan).fillna("Unknown")
        quality_log["missing_values_filled"][text_col] = before_missing

    working_df["quantity"] = _to_numeric(working_df["quantity"])
    working_df["unit_price"] = _to_numeric(working_df["unit_price"])
    working_df["revenue"] = _to_numeric(working_df["revenue"])

    negative_quantity = int((working_df["quantity"] < 0).sum())
    negative_price = int((working_df["unit_price"] < 0).sum())
    if negative_quantity > 0:
        working_df.loc[working_df["quantity"] < 0, "quantity"] = np.nan
    if negative_price > 0:
        working_df.loc[working_df["unit_price"] < 0, "unit_price"] = np.nan

    quantity_fill = int(working_df["quantity"].isna().sum())
    unit_price_fill = int(working_df["unit_price"].isna().sum())

    quantity_default = max(1.0, float(np.nanmedian(working_df["quantity"])) if not working_df["quantity"].dropna().empty else 1.0)
    unit_price_default = float(np.nanmedian(working_df["unit_price"])) if not working_df["unit_price"].dropna().empty else 0.0

    working_df["quantity"] = working_df["quantity"].fillna(quantity_default).round().astype(int)
    working_df["unit_price"] = working_df["unit_price"].fillna(unit_price_default).round(2)

    quality_log["missing_values_filled"]["quantity"] = quantity_fill
    quality_log["missing_values_filled"]["unit_price"] = unit_price_fill

    calculated_revenue = (working_df["quantity"] * working_df["unit_price"]).round(2)
    revenue_missing = working_df["revenue"].isna()
    revenue_mismatch = (~revenue_missing) & ((working_df["revenue"] - calculated_revenue).abs() > 0.01)
    recalculated_rows = int((revenue_missing | revenue_mismatch).sum())

    working_df["revenue"] = calculated_revenue
    quality_log["revenue_recalculated_rows"] = recalculated_rows

    dedup_keys = ["order_id", "order_date", "product_name", "customer_name"]
    if quality_log["generated_order_ids"] >= len(working_df):
        # If IDs are fully synthetic, dedupe by business attributes excluding order_id.
        dedup_keys = ["order_date", "product_name", "customer_name", "category", "quantity", "unit_price"]
    before_dedup = len(working_df)
    working_df = working_df.drop_duplicates(subset=dedup_keys, keep="first").copy()
    quality_log["duplicate_rows_removed"] = int(before_dedup - len(working_df))

    working_df = working_df.sort_values("order_date").reset_index(drop=True)
    working_df = working_df[CANONICAL_COLUMNS]

    quality_log["rows_final"] = int(len(working_df))

    if quality_log["missing_columns_added"]:
        quality_log["notes"].append(
            "Added missing columns with defaults: " + ", ".join(quality_log["missing_columns_added"])
        )

    if len(working_df) == 0:
        quality_log["notes"].append("All rows were removed during validation and cleaning.")

    return working_df, quality_log
