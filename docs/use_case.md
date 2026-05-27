# Use Case Document

## 1. Actor
- Primary Actor: Business Analyst
- Secondary Actors: Sales Manager, Finance Reviewer

## 2. Use Case List
1. Upload Sales Data
2. Clean and Standardize Data
3. Analyze KPIs and Trends
4. Filter Dashboard
5. Export Professional Excel Report
6. Persist Data to MySQL (Non-blocking)

## 3. Main Flow
1. Actor opens the Streamlit dashboard.
2. Actor selects sample dataset or uploads a CSV/Excel file.
3. System validates format and loads raw data.
4. System cleans and standardizes the dataset.
5. System calculates KPIs and generates business insights.
6. Actor applies filters (month/category/product).
7. System refreshes KPI cards, charts, and cleaned data table.
8. Actor clicks export button.
9. System creates professional Excel report in `reports/`.
10. System attempts to save cleaned data and KPI snapshot into MySQL.
11. System shows success/warning messages.

## 4. Alternative Flow
### A1 - Invalid File Type
- At step 2, actor uploads unsupported format.
- System shows clear error message and asks for CSV/XLS/XLSX.

### A2 - Empty File
- At step 3, source file has no usable rows.
- System warns user and stops analysis flow.

### A3 - Severe Data Quality Issue
- At step 4, all rows become invalid after cleaning.
- System displays error and prevents KPI/export.

### A4 - MySQL Unavailable
- At step 10, DB connection/write fails.
- System still keeps dashboard/export successful and shows non-blocking warning.
