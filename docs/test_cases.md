# Test Cases

| Test Case ID | Test Scenario | Steps | Expected Result |
|---|---|---|---|
| TC-001 | Upload valid CSV file | 1. Open app 2. Upload `.csv` with required sales fields | Data loads successfully and dashboard renders KPIs/charts |
| TC-002 | Upload valid Excel file | 1. Open app 2. Upload `.xlsx` file | Data loads successfully and dashboard renders KPIs/charts |
| TC-003 | Upload invalid file type | 1. Upload `.txt` or unsupported format | System shows upload validation error message |
| TC-004 | Handle missing order_id | 1. Upload data without `order_id` | System generates `AUTO-######` IDs and logs note in quality log |
| TC-005 | Remove invalid dates | 1. Upload data with malformed dates | Rows with invalid dates are removed; count reflected in quality summary |
| TC-006 | Normalize numeric fields | 1. Upload data containing `$`, commas, and text in numeric columns | System converts valid values, fills invalid values by cleaning rules |
| TC-007 | Revenue recalculation | 1. Upload data with missing/inconsistent revenue | Revenue recalculated as `quantity * unit_price` |
| TC-008 | Duplicate handling | 1. Upload data containing duplicate business keys | Duplicates removed and counted in quality log |
| TC-009 | KPI correctness | 1. Load deterministic test dataset 2. Compare KPI outputs | KPI formulas return expected values |
| TC-010 | Sidebar filter behavior | 1. Select month/category/product filters | KPI cards, charts, and table update consistently |
| TC-011 | Export Excel report | 1. Click export button | Report created in `reports/` with required sheets and formatting |
| TC-012 | MySQL write failure handling | 1. Use wrong DB credentials 2. Export report | Excel still exported; DB warning shown without app crash |
| TC-013 | Cleaned data sheet integrity | 1. Export after cleaning | `Cleaned_Data` sheet exists and contains standardized canonical columns |
| TC-014 | Data quality log export | 1. Export after cleaning | `Data_Quality_Log` sheet includes key cleaning counters and notes |
