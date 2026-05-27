from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


COLOR_PRIMARY = "#0F766E"
COLOR_SECONDARY = "#0EA5E9"
COLOR_ACCENT = "#F59E0B"


def _empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")
    fig.update_layout(template="plotly_white", xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig


def create_monthly_revenue_chart(revenue_by_month: pd.DataFrame) -> go.Figure:
    if revenue_by_month.empty:
        return _empty_figure("No month-level data to display.")

    fig = px.line(
        revenue_by_month,
        x="month",
        y="revenue",
        markers=True,
        title="Revenue Trend by Month",
        color_discrete_sequence=[COLOR_PRIMARY],
    )
    fig.update_layout(template="plotly_white", xaxis_title="Month", yaxis_title="Revenue")
    return fig


def create_top_products_chart(top_products: pd.DataFrame) -> go.Figure:
    if top_products.empty:
        return _empty_figure("No product data to display.")

    fig = px.bar(
        top_products.sort_values("revenue", ascending=True),
        x="revenue",
        y="product_name",
        orientation="h",
        title="Top 5 Products by Revenue",
        color_discrete_sequence=[COLOR_SECONDARY],
    )
    fig.update_layout(template="plotly_white", xaxis_title="Revenue", yaxis_title="Product")
    return fig


def create_category_performance_chart(revenue_by_category: pd.DataFrame) -> go.Figure:
    if revenue_by_category.empty:
        return _empty_figure("No category data to display.")

    fig = px.bar(
        revenue_by_category,
        x="category",
        y="revenue",
        title="Revenue by Category",
        color="category",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(template="plotly_white", xaxis_title="Category", yaxis_title="Revenue", showlegend=False)
    return fig


def create_category_share_chart(revenue_by_category: pd.DataFrame) -> go.Figure:
    if revenue_by_category.empty:
        return _empty_figure("No category share to display.")

    fig = px.pie(
        revenue_by_category,
        names="category",
        values="revenue",
        title="Category Revenue Share",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(template="plotly_white")
    return fig
