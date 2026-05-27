# Business Requirement Document (BRD)

## 1. Business Problem
Business stakeholders lack a lightweight and consistent way to analyze sales performance from ad-hoc CSV/Excel files. Data quality issues (missing values, invalid dates, inconsistent numeric formats) create unreliable KPI reporting and delayed decision making.

## 2. Project Objective
Build a portfolio-ready Sales Analytics Dashboard that enables Business Analysts to:
- Upload sales files quickly.
- Clean and standardize data automatically.
- Monitor core sales KPIs and trends.
- Generate actionable business insights.
- Export a professional Excel report for stakeholders.

## 3. Stakeholders
- Business Analyst (primary user)
- Sales Manager
- Finance Team
- Data/IT Team

## 4. Scope
### In Scope
- CSV/Excel upload.
- Automated cleaning and standardization.
- KPI computation and visual analytics.
- Interactive filtering by month/category/product.
- Professional Excel report export.
- Optional MySQL persistence (balanced mode).

### Out of Scope
- Real-time streaming data ingestion.
- Role-based authentication/authorization.
- Predictive forecasting models.

## 5. Functional Requirements
1. User can upload CSV/XLS/XLSX sales files.
2. System validates file type and handles invalid input errors.
3. System standardizes columns into canonical schema.
4. System cleans missing values, date formats, numeric fields, and duplicates.
5. System computes KPIs:
   - Total Revenue
   - Total Orders
   - Average Order Value
   - Total Quantity Sold
   - Monthly Growth Rate
   - Top 5 Products
   - Top 5 Customers
   - Revenue by Month
   - Revenue by Category
6. User can filter dashboard by month, category, and product.
7. Dashboard displays KPI cards, charts, cleaned table, and auto-generated business insights.
8. User can export a professional Excel report to `reports/`.
9. System attempts to save cleaned data and KPI snapshot to MySQL without blocking UI when DB errors occur.

## 6. Non-Functional Requirements
- Performance: Dashboard should load and respond quickly for ~1,000 to ~10,000 rows.
- Reliability: Invalid uploads should produce clear, recoverable error messages.
- Maintainability: Modular codebase with separate data, KPI, visualization, and export layers.
- Usability: Business-friendly UI and clear labels.
- Portability: Run locally via Python virtual environment and Streamlit.

## 7. Business Rules
1. Canonical schema includes:
   `order_id, order_date, customer_name, product_name, category, quantity, unit_price, revenue`.
2. If `order_id` is missing, system generates `AUTO-######` identifiers.
3. Rows with invalid `order_date` are removed.
4. Negative `quantity` and `unit_price` values are treated as invalid and replaced during cleaning.
5. `revenue` is recalculated as `quantity * unit_price` when missing or inconsistent.
6. Duplicates are removed by business key:
   `order_id + order_date + product_name + customer_name`.
7. Monthly growth rate is computed month-over-month based on filtered data.

## 8. KPI Definitions
- **Total Revenue**: Sum of `revenue`.
- **Total Orders**: Distinct count of `order_id`.
- **Average Order Value (AOV)**: `Total Revenue / Total Orders`.
- **Total Quantity Sold**: Sum of `quantity`.
- **Monthly Growth Rate**: `(Current Month Revenue - Previous Month Revenue) / Previous Month Revenue`.
- **Top 5 Products**: Products ranked by revenue descending.
- **Top 5 Customers**: Customers ranked by revenue descending.
- **Revenue by Month**: Monthly aggregated revenue.
- **Revenue by Category**: Category-level aggregated revenue.
