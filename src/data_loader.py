from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any
import os
import re
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


CANONICAL_COLUMNS = [
    "order_id",
    "order_date",
    "customer_name",
    "product_name",
    "category",
    "quantity",
    "unit_price",
    "revenue",
]

_COLUMN_ALIASES = {
    "orderid": "order_id",
    "order_id": "order_id",
    "order": "order_id",
    "ordernumber": "order_id",
    "order_no": "order_id",
    "date": "order_date",
    "orderdate": "order_date",
    "order_date": "order_date",
    "sale_date": "order_date",
    "customer": "customer_name",
    "customername": "customer_name",
    "customer_name": "customer_name",
    "client": "customer_name",
    "product": "product_name",
    "productname": "product_name",
    "product_name": "product_name",
    "item": "product_name",
    "category": "category",
    "segment": "category",
    "qty": "quantity",
    "quantity": "quantity",
    "units": "quantity",
    "unit_price": "unit_price",
    "price": "unit_price",
    "unitprice": "unit_price",
    "selling_price": "unit_price",
    "revenue": "revenue",
    "sales": "revenue",
    "amount": "revenue",
    "total": "revenue",
}


class DataLoaderError(Exception):
    """Raised when data loading fails due to invalid input."""


def _normalize_token(text: str) -> str:
    return "".join(ch for ch in text.strip().lower().replace(" ", "_") if ch.isalnum() or ch == "_")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename input columns into canonical names and merge duplicated canonical targets."""
    normalized_labels: list[str] = []
    for col in df.columns:
        token = _normalize_token(str(col))
        normalized_labels.append(_COLUMN_ALIASES.get(token, token))

    normalized_df = pd.DataFrame(index=df.index)
    seen: set[str] = set()
    for idx, canonical in enumerate(normalized_labels):
        if canonical in seen:
            continue
        seen.add(canonical)
        duplicate_indexes = [i for i, label in enumerate(normalized_labels) if label == canonical]
        if len(duplicate_indexes) == 1:
            normalized_df[canonical] = df.iloc[:, duplicate_indexes[0]]
        else:
            normalized_df[canonical] = df.iloc[:, duplicate_indexes].bfill(axis=1).iloc[:, 0]

    return normalized_df


def _load_from_path(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise DataLoaderError("Unsupported file type. Please upload a CSV or Excel file.")


def _load_from_uploaded_file(file: Any) -> pd.DataFrame:
    if not hasattr(file, "name"):
        raise DataLoaderError("Uploaded object is invalid.")

    suffix = Path(file.name).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(file)
    if suffix in {".xlsx", ".xls"}:
        content = file.read()
        return pd.read_excel(BytesIO(content))
    raise DataLoaderError("Unsupported file type. Please upload a CSV or Excel file.")


def load_sales_data(file_or_path: Any) -> pd.DataFrame:
    """Load raw sales data from local path or Streamlit uploaded file."""
    try:
        if isinstance(file_or_path, (str, Path)):
            raw_df = _load_from_path(Path(file_or_path))
        else:
            raw_df = _load_from_uploaded_file(file_or_path)

        if raw_df.empty:
            raise DataLoaderError("The provided file is empty.")

        normalized_df = normalize_columns(raw_df)
        return normalized_df
    except DataLoaderError:
        raise
    except Exception as exc:
        raise DataLoaderError(f"Failed to load dataset: {exc}") from exc


def get_db_config() -> dict[str, str]:
    """Read MySQL settings from environment variables."""
    load_dotenv(override=False)
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "3306"),
        "name": os.getenv("DB_NAME", "sales_analytics"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def _sanitize_db_name(database_name: str) -> str:
    cleaned_name = database_name.strip()
    if not cleaned_name:
        raise ValueError("Database name cannot be empty.")
    if not re.fullmatch(r"[A-Za-z0-9_\\-]+", cleaned_name):
        raise ValueError("Database name contains unsupported characters.")
    return cleaned_name


def _build_mysql_url(db_config: dict[str, str], include_database: bool = True) -> str:
    user = quote_plus(db_config["user"])
    password = quote_plus(db_config["password"])
    host = db_config["host"]
    port = db_config["port"]

    if include_database:
        database_name = _sanitize_db_name(db_config["name"])
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database_name}"
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/"


def create_mysql_engine(db_config: dict[str, str], create_db_if_missing: bool = True) -> Engine:
    """Create SQLAlchemy engine for MySQL and auto-create database if configured."""
    required_keys = {"host", "port", "name", "user", "password"}
    missing = sorted(k for k in required_keys if not db_config.get(k) and k != "password")
    if missing:
        raise ValueError(f"Missing DB config keys: {', '.join(missing)}")

    db_url = _build_mysql_url(db_config, include_database=True)
    engine = create_engine(db_url, pool_pre_ping=True)

    if not create_db_if_missing:
        return engine

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return engine
    except Exception as exc:
        error_text = str(exc).lower()
        if "unknown database" not in error_text and "1049" not in error_text:
            raise

    admin_engine = create_engine(_build_mysql_url(db_config, include_database=False), pool_pre_ping=True)
    database_name = _sanitize_db_name(db_config["name"])
    with admin_engine.connect() as connection:
        connection.execute(
            text(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        )
        connection.commit()
    admin_engine.dispose()

    engine = create_engine(db_url, pool_pre_ping=True)
    return engine
