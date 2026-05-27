from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src.data_cleaning import clean_sales_data
from src.data_loader import CANONICAL_COLUMNS, DataLoaderError, get_db_config, load_sales_data
from src.kpi_calculator import calculate_kpis
from src.report_exporter import export_summary_report, save_to_mysql
from src.visualization import (
    create_category_performance_chart,
    create_category_share_chart,
    create_monthly_revenue_chart,
    create_top_products_chart,
)


PLOTLY_CONFIG = {
    "displaylogo": False,
    "scrollZoom": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}


st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="SA",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --bg-soft: #f6f8fc;
        --ink-strong: #0f172a;
        --ink-muted: #475569;
        --brand: #0f766e;
        --brand-soft: #d7f9f1;
        --border-soft: #dbe4ef;
    }

    html, body, [class*="css"] {
        font-family: "Manrope", "Segoe UI", sans-serif;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 0% 0%, rgba(14, 165, 233, 0.08), transparent 30%),
            radial-gradient(circle at 95% 5%, rgba(15, 118, 110, 0.08), transparent 28%),
            var(--bg-soft);
    }

    /* Force strong contrast in main content area */
    [data-testid="stMainBlockContainer"] {
        color: #0f172a !important;
    }

    [data-testid="stMainBlockContainer"] p,
    [data-testid="stMainBlockContainer"] label,
    [data-testid="stMainBlockContainer"] li,
    [data-testid="stMainBlockContainer"] div,
    [data-testid="stMainBlockContainer"] span {
        color: #0f172a;
    }

    [data-testid="stMainBlockContainer"] .stMetric label,
    [data-testid="stMainBlockContainer"] .stMetric [data-testid="stMetricValue"] {
        color: #0f172a !important;
    }

    [data-testid="stMainBlockContainer"] button[kind="secondary"] {
        background: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
    }

    [data-testid="stMainBlockContainer"] button[kind="secondary"] p,
    [data-testid="stMainBlockContainer"] button[kind="secondary"] span {
        color: #0f172a !important;
    }

    .hero-wrap {
        background: linear-gradient(130deg, #0f172a 0%, #1e293b 45%, #0f766e 130%);
        border-radius: 18px;
        padding: 22px 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.18);
        margin-bottom: 14px;
    }

    .hero-wrap, .hero-wrap * {
        color: #f8fafc !important;
    }

    .hero-title {
        margin: 0;
        color: #f8fafc;
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: 0.2px;
    }

    .hero-subtitle {
        margin-top: 6px;
        margin-bottom: 14px;
        color: #cbd5e1;
        font-size: 0.97rem;
        max-width: 900px;
    }

    .hero-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .hero-chip {
        background: rgba(15, 23, 42, 0.38);
        color: #dbeafe;
        border: 1px solid rgba(148, 163, 184, 0.32);
        border-radius: 999px;
        padding: 5px 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .section-title {
        color: var(--ink-strong);
        font-size: 1.08rem;
        font-weight: 800;
        margin-bottom: 2px;
    }

    .section-subtitle {
        color: var(--ink-muted);
        font-size: 0.86rem;
        margin-bottom: 8px;
    }

    .kpi-card {
        border: 1px solid var(--border-soft);
        border-radius: 14px;
        padding: 14px;
        background: linear-gradient(155deg, #ffffff 0%, #f8fbff 100%);
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
        min-height: 118px;
    }

    .kpi-label {
        color: #334155;
        font-size: 0.84rem;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .kpi-value {
        color: #0f172a;
        font-size: 1.34rem;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .kpi-footnote {
        color: #64748b;
        font-size: 0.75rem;
        line-height: 1.25;
    }

    .context-pill {
        border: 1px solid #d6e2f2;
        border-radius: 12px;
        padding: 10px 12px;
        background: #f8fbff;
        min-height: 72px;
    }

    .context-label {
        color: #64748b;
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.35px;
    }

    .context-value {
        margin-top: 3px;
        color: #0f172a;
        font-size: 1.02rem;
        font-weight: 800;
    }

    .insight-card {
        border: 1px solid #d5e7ff;
        border-left: 4px solid #0ea5e9;
        border-radius: 10px;
        background: #f8fcff;
        padding: 10px 12px;
        margin-bottom: 8px;
        color: #0f172a;
        font-size: 0.87rem;
        line-height: 1.35;
    }

    .export-note {
        background: #eefcf9;
        border: 1px solid #a7f3d0;
        border-radius: 10px;
        padding: 10px 12px;
        color: #14532d;
        font-size: 0.84rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.26);
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #e2e8f0;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 23, 42, 0.50);
        border-radius: 14px;
        border: 1px solid rgba(148, 163, 184, 0.28);
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: #0f766e !important;
        border-radius: 999px !important;
        border: 0 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] span {
        color: #ecfeff !important;
    }

    [data-testid="stSidebar"] .stAlert {
        background: rgba(22, 101, 52, 0.30);
        border: 1px solid rgba(74, 222, 128, 0.45);
    }

    .sidebar-caption {
        font-size: 0.78rem;
        color: #94a3b8;
        line-height: 1.3;
    }

    [data-baseweb="tab-list"] {
        gap: 6px;
    }

    [data-baseweb="tab"] {
        border: 1px solid #d7e2f2;
        border-radius: 10px 10px 0 0;
        padding: 8px 14px;
        font-weight: 700;
        background: #f2f6fd;
    }

    [aria-selected="true"][data-baseweb="tab"] {
        background: #ffffff;
        border-color: #b5c9e6;
    }

    .stDataFrame {
        border: 1px solid #dbe5f1;
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _render_hero() -> None:
    now_label = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(
        f"""
        <div class="hero-wrap">
            <h1 class="hero-title">Sales Analytics Dashboard</h1>
            <p class="hero-subtitle">
                BA-oriented analytics workspace with data cleaning traceability, KPI insights, visual storytelling, and professional report export.
            </p>
            <div class="hero-chip-row">
                <span class="hero-chip">Streamlit + Plotly</span>
                <span class="hero-chip">Pandas Data Quality Pipeline</span>
                <span class="hero-chip">MySQL Balanced Persistence</span>
                <span class="hero-chip">Refreshed at {now_label}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_section_header(title: str, subtitle: str) -> None:
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def _render_kpi_card(label: str, value: str, footnote: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-footnote">{footnote}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_context_pill(label: str, value: str) -> str:
    return (
        "<div class='context-pill'>"
        f"<div class='context-label'>{label}</div>"
        f"<div class='context-value'>{value}</div>"
        "</div>"
    )


def _format_growth(growth_value: Any) -> str:
    if pd.isna(growth_value):
        return "N/A"
    return f"{float(growth_value) * 100:,.2f}%"


def _quality_log_to_df(quality_log: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key, value in quality_log.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                rows.append({"metric": f"{key}.{sub_key}", "value": sub_value})
        elif isinstance(value, list):
            rows.append({"metric": key, "value": " | ".join(str(v) for v in value)})
        else:
            rows.append({"metric": key, "value": value})
    quality_df = pd.DataFrame(rows)
    if not quality_df.empty:
        quality_df["value"] = quality_df["value"].astype(str)
    return quality_df


def _render_filter_block(title: str, options: list[str], key_prefix: str, default_all: bool = True) -> list[str]:
    filter_container = st.sidebar.container(border=True)
    with filter_container:
        st.markdown(f"**{title}**")
        if not options:
            st.caption("No options available from current dataset.")
            return []

        select_all = st.checkbox(
            f"Use all {title.lower()}",
            value=default_all,
            key=f"{key_prefix}_all",
        )

        if select_all:
            st.markdown(
                f"<div class='sidebar-caption'>Using all {len(options)} {title.lower()}.</div>",
                unsafe_allow_html=True,
            )
            return options

        selected_values = st.multiselect(
            label=f"Select {title}",
            options=options,
            default=options[: min(4, len(options))],
            key=f"{key_prefix}_values",
            placeholder=f"Choose {title.lower()}...",
            label_visibility="collapsed",
        )

        if not selected_values:
            st.markdown(
                f"<div class='sidebar-caption'>No custom selection yet. Fallback to all {title.lower()}.</div>",
                unsafe_allow_html=True,
            )
            return options

        st.markdown(
            f"<div class='sidebar-caption'>{len(selected_values)} selected.</div>",
            unsafe_allow_html=True,
        )
        return selected_values


def _filter_data(clean_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    filtered_df = clean_df.copy()
    filtered_df["month"] = filtered_df["order_date"].dt.to_period("M").astype(str)

    st.sidebar.markdown("### Filters")
    st.sidebar.markdown(
        "<div class='sidebar-caption'>Use the toggles to keep filters compact, then switch to custom picks only when needed.</div>",
        unsafe_allow_html=True,
    )

    month_options = sorted(filtered_df["month"].dropna().unique().tolist())
    selected_months = _render_filter_block("Month", month_options, "months")

    category_options = sorted(filtered_df["category"].dropna().unique().tolist())
    selected_categories = _render_filter_block("Category", category_options, "categories")

    product_options = sorted(filtered_df["product_name"].dropna().unique().tolist())
    selected_products = _render_filter_block("Product", product_options, "products")

    if selected_months:
        filtered_df = filtered_df[filtered_df["month"].isin(selected_months)]
    if selected_categories:
        filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]
    if selected_products:
        filtered_df = filtered_df[filtered_df["product_name"].isin(selected_products)]

    filtered_df = filtered_df.drop(columns=["month"]) if "month" in filtered_df.columns else filtered_df

    selected_filters = {
        "months": selected_months,
        "categories": selected_categories,
        "products": selected_products,
    }
    return filtered_df, selected_filters


def main() -> None:
    _render_hero()

    st.sidebar.markdown("## Control Center")
    st.sidebar.markdown(
        "<div class='sidebar-caption'>Select data source, tune filters, and generate stakeholder-ready outputs.</div>",
        unsafe_allow_html=True,
    )

    with st.sidebar.container(border=True):
        st.markdown("### Data Source")
        source_option = st.radio(
            "Choose source",
            ["Use Sample Dataset", "Upload File"],
            help="Sample data is ideal for quick demo. Upload mode supports CSV/XLS/XLSX.",
        )

        sample_file_path = Path("data") / "sample_sales_data.xlsx"
        raw_df: pd.DataFrame | None = None
        source_label = "Sample Dataset"

        try:
            if source_option == "Use Sample Dataset":
                raw_df = load_sales_data(sample_file_path)
                st.success("Sample dataset loaded")
            else:
                uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
                if uploaded_file is not None:
                    raw_df = load_sales_data(uploaded_file)
                    source_label = uploaded_file.name
                else:
                    st.info("Upload a file to start analysis, or switch back to sample dataset.")
                    return
        except DataLoaderError as exc:
            st.error(f"Upload error: {exc}")
            return
        except Exception as exc:
            st.error(f"Unexpected loading error: {exc}")
            return

    if raw_df is None or raw_df.empty:
        st.warning("No data available for processing.")
        return

    clean_df, quality_log = clean_sales_data(raw_df)
    if clean_df.empty:
        st.error("All rows were removed during cleaning. Please provide a better-quality dataset.")
        return

    filtered_df, selected_filters = _filter_data(clean_df)
    kpis = calculate_kpis(filtered_df)

    with st.container(border=True):
        _render_section_header("Analysis Context", "Quick status after cleaning and current filters.")
        p1, p2, p3, p4 = st.columns(4)
        p1.markdown(_render_context_pill("Data Source", source_label), unsafe_allow_html=True)
        p2.markdown(_render_context_pill("Rows in Scope", f"{len(filtered_df):,}"), unsafe_allow_html=True)
        p3.markdown(_render_context_pill("Months Selected", f"{len(selected_filters['months']):,}"), unsafe_allow_html=True)
        p4.markdown(
            _render_context_pill("Categories Selected", f"{len(selected_filters['categories']):,}"),
            unsafe_allow_html=True,
        )

    tab_overview, tab_segments, tab_data = st.tabs(["Overview", "Products & Customers", "Data Quality & Export"])

    with tab_overview:
        _render_section_header("KPI Snapshot", "Core business performance indicators from the active filtered dataset.")
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            _render_kpi_card("Total Revenue", f"${kpis['total_revenue']:,.2f}", "Sum of revenue across filtered records")
        with c2:
            _render_kpi_card("Total Orders", f"{kpis['total_orders']:,}", "Distinct order_id count")
        with c3:
            _render_kpi_card("Average Order Value", f"${kpis['average_order_value']:,.2f}", "Revenue divided by total orders")
        with c4:
            _render_kpi_card("Total Quantity Sold", f"{kpis['total_quantity_sold']:,}", "Total units sold")
        with c5:
            _render_kpi_card("Monthly Growth Rate", _format_growth(kpis["monthly_growth_rate"]), "Latest MoM growth")

        with st.container(border=True):
            _render_section_header("Business Insights", "Auto-generated interpretations to support BA storytelling.")
            for insight in kpis.get("insights", []):
                st.markdown(f"<div class='insight-card'>{insight}</div>", unsafe_allow_html=True)

        left_col, right_col = st.columns(2)
        with left_col:
            st.plotly_chart(
                create_monthly_revenue_chart(kpis["revenue_by_month"]),
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )
            st.plotly_chart(
                create_category_performance_chart(kpis["revenue_by_category"]),
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )
        with right_col:
            st.plotly_chart(
                create_top_products_chart(kpis["top_products"]),
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )
            st.plotly_chart(
                create_category_share_chart(kpis["revenue_by_category"]),
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

    with tab_segments:
        _render_section_header("Product and Customer Segments", "Review top contributors and concentration patterns.")
        seg_left, seg_right = st.columns(2)

        with seg_left:
            with st.container(border=True):
                st.markdown("#### Top 5 Products")
                st.dataframe(
                    kpis["top_products"],
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "revenue": st.column_config.NumberColumn("Revenue", format="$%,.2f"),
                        "quantity": st.column_config.NumberColumn("Quantity", format="%,d"),
                    },
                )

            with st.container(border=True):
                st.markdown("#### Revenue by Category")
                st.dataframe(
                    kpis["revenue_by_category"],
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "revenue": st.column_config.NumberColumn("Revenue", format="$%,.2f"),
                    },
                )

        with seg_right:
            with st.container(border=True):
                st.markdown("#### Top 5 Customers")
                st.dataframe(
                    kpis["top_customers"],
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "revenue": st.column_config.NumberColumn("Revenue", format="$%,.2f"),
                        "orders": st.column_config.NumberColumn("Orders", format="%,d"),
                    },
                )

            with st.container(border=True):
                st.markdown("#### Revenue by Month")
                st.dataframe(
                    kpis["revenue_by_month"],
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "revenue": st.column_config.NumberColumn("Revenue", format="$%,.2f"),
                    },
                )

    with tab_data:
        _render_section_header("Data Quality", "Track cleaning outcomes before reporting and export.")
        q1, q2, q3, q4 = st.columns(4)
        q1.metric("Rows (Initial)", f"{quality_log['rows_initial']:,}")
        q2.metric("Rows (Final)", f"{quality_log['rows_final']:,}")
        q3.metric("Invalid Dates Removed", f"{quality_log['invalid_date_rows_removed']:,}")
        q4.metric("Duplicates Removed", f"{quality_log['duplicate_rows_removed']:,}")

        with st.expander("View full data quality log", expanded=False):
            quality_log_df = _quality_log_to_df(quality_log)
            st.dataframe(quality_log_df, width="stretch", hide_index=True)

        st.markdown("#### Cleaned Data Preview")
        st.dataframe(
            filtered_df,
            width="stretch",
            height=360,
            hide_index=True,
            column_config={
                "order_date": st.column_config.DateColumn("Order Date", format="YYYY-MM-DD"),
                "quantity": st.column_config.NumberColumn("Quantity", format="%,d"),
                "unit_price": st.column_config.NumberColumn("Unit Price", format="$%,.2f"),
                "revenue": st.column_config.NumberColumn("Revenue", format="$%,.2f"),
            },
        )

        with st.container(border=True):
            st.markdown("#### Export Professional Report")
            st.markdown(
                "<div class='export-note'>Exports the current filtered view with KPI summary, business insights, and data quality log to an Excel workbook in reports/.</div>",
                unsafe_allow_html=True,
            )

            can_export = (not filtered_df.empty) and set(CANONICAL_COLUMNS).issubset(filtered_df.columns)
            if not can_export:
                st.warning("Cannot export: dataset is empty or missing required columns.")
            else:
                btn_col, info_col = st.columns([1.3, 2])
                with btn_col:
                    if st.button("Export Professional Excel Report", type="primary", width="stretch"):
                        with st.spinner("Generating report..."):
                            report_path = export_summary_report(
                                clean_df=filtered_df,
                                kpis=kpis,
                                charts_data={"filters": selected_filters},
                                quality_log=quality_log,
                                output_dir="reports",
                            )

                            db_saved, db_message = save_to_mysql(filtered_df, kpis, get_db_config())

                            st.session_state["last_report_path"] = report_path
                            st.session_state["last_db_status"] = (db_saved, db_message)

                with info_col:
                    report_path = st.session_state.get("last_report_path")
                    db_status = st.session_state.get("last_db_status")

                    if report_path:
                        st.success(f"Excel report created: {report_path}")
                        if Path(report_path).exists():
                            with open(report_path, "rb") as file_obj:
                                st.download_button(
                                    label="Download Latest Report",
                                    data=file_obj.read(),
                                    file_name=Path(report_path).name,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    width="stretch",
                                )

                    if db_status:
                        db_saved, db_message = db_status
                        if db_saved:
                            st.success(db_message)
                        else:
                            st.warning(db_message)


if __name__ == "__main__":
    main()
