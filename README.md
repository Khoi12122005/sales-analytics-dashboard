# Sales Analytics Dashboard

A portfolio-grade analytics application that demonstrates **Business Analysis thinking + Python engineering execution** from raw sales files to decision-ready insights.

## Live Demo
- [Full Streamlit Dashboard (temporary public URL)](https://mighty-resolve-univ-trek.trycloudflare.com)
- [Vercel Landing Page](https://sales-analytics-dashboard-ochre.vercel.app)
- [Health Endpoint](https://sales-analytics-dashboard-ochre.vercel.app/health)
- [GitHub Repository](https://github.com/Khoi12122005/sales-analytics-dashboard)

> Note: The `trycloudflare` link above is a temporary public URL for the full Streamlit runtime.
> If it expires, run `scripts/start_public_demo.ps1` to generate a new public URL instantly.
> The Vercel URL is a landing/API endpoint, not the full Streamlit runtime.

## What This Project Delivers
- Upload and analyze sales data from `.csv`, `.xlsx`, `.xls`
- Clean and standardize inconsistent datasets with a traceable quality log
- Calculate business KPIs and auto-generate actionable insights
- Explore results in an interactive Streamlit + Plotly dashboard
- Export a polished multi-sheet Excel report for stakeholders
- Persist cleaned snapshots to MySQL (non-blocking if DB is unavailable)

## Business Value
This project is designed for **BA/IT portfolio presentation** and shows:
- Requirement analysis and KPI definition
- Data quality governance and rule-based cleansing
- Decision support through trend and segment analysis
- Professional reporting workflow for business users

## KPI Coverage
- Total Revenue
- Total Orders
- Average Order Value (AOV)
- Total Quantity Sold
- Monthly Growth Rate (MoM)
- Top 5 Products
- Top 5 Customers
- Revenue by Month
- Revenue by Category

## Tech Stack
- Python
- Pandas, NumPy
- Streamlit
- Plotly
- OpenPyXL
- MySQL + SQLAlchemy + PyMySQL
- Pytest

## Repository Structure
```text
sales-analytics-dashboard/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .streamlit/
│   └── config.toml
├── data/
│   └── sample_sales_data.xlsx
├── src/
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── kpi_calculator.py
│   ├── visualization.py
│   └── report_exporter.py
├── reports/
├── docs/
│   ├── business_requirement.md
│   ├── use_case.md
│   └── test_cases.md
└── tests/
    ├── test_data_cleaning.py
    ├── test_kpi_calculator.py
    └── test_report_exporter.py
```

## Data Cleaning Rules (Core Contract)
Canonical schema after cleaning:
- `order_id`, `order_date`, `customer_name`, `product_name`, `category`, `quantity`, `unit_price`, `revenue`

Business rules:
- Auto-create `order_id` when missing
- Remove invalid dates
- Normalize numeric fields (`quantity`, `unit_price`, `revenue`)
- Replace invalid/negative numeric values by rule
- Recalculate revenue using `quantity * unit_price`
- Remove duplicates by business key

## Excel Report Output
Exports a professional workbook to `reports/` with:
- `Executive_Summary`
- `KPI_Summary`
- `Revenue_By_Month`
- `Revenue_By_Category`
- `Top_Products`
- `Top_Customers`
- `Cleaned_Data`
- `Data_Quality_Log`

## MySQL Setup
1. Copy `.env.example` to `.env`
2. Configure your credentials:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=sales_analytics
DB_USER=root
DB_PASSWORD=your_password
```

Note: The app attempts to auto-create the database if missing. If MySQL is unavailable, dashboard/export still works.

## Run Locally (VS Code)
From project root:

```powershell
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests
```powershell
pytest -q
```

## BA Documentation
Located in `docs/`:
- `business_requirement.md`
- `use_case.md`
- `test_cases.md`

## Deployment Note
This app is a **Streamlit server app**. Vercel is optimized for serverless web functions and is not a native host for long-running Streamlit services.

Recommended production/demo hosting for full dashboard runtime:
- Streamlit Community Cloud
- Render
- Railway

## Author
Developed as a practical BA + Python portfolio project focused on real business reporting workflows.
