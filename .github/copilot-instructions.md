# Sales Analytics System - AI Agent Guidelines

## Project Overview
A Python-based ETL pipeline that processes raw sales data, validates/cleans records, and generates multi-format reports with optional API enrichment. Data flows through three stages: **parsing → validation → enrichment/reporting**.

## Architecture & Data Flow

### Core Pipeline (main.py)
1. **Read** raw sales data from `data/sales_data.txt` (8 pipe-delimited fields)
2. **Parse** into dictionaries, handling encoding and format issues
3. **Validate** against strict ID format rules (T/P/C prefixes) and value constraints
4. **Filter** optionally by region or transaction amount
5. **Enrich** by fetching external product metadata (API handler)
6. **Report** in two formats: basic region summary and comprehensive analytics report

### Key Data Schema
Raw transaction fields: `TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region`
- **ID Validation**: TransactionID must start with "T", ProductID with "P", CustomerID with "C"
- **Numeric Handling**: Quantity as int, UnitPrice as float; commas are stripped before conversion
- **Invalid Records**: Removed if Quantity ≤ 0, UnitPrice ≤ 0, or ID format invalid

### Enrichment Flow (api_handler.py)
- **Local Mapping**: `fetch_product_info()` uses hardcoded category dict (P101→Laptop, etc.)
- **API Enrichment**: `fetch_all_products()` fetches from DummyJSON, creates numeric ID mapping
- **Attach Fields**: Adds `API_Category`, `API_Brand`, `API_Rating`, `API_Match` to transactions
- **Save Format**: Enriched data written to `data/enriched_sales_data.txt` with 12 pipe-delimited fields

## Critical Conventions & Patterns

### Encoding Robustness
File handler tries multiple encodings (utf-8 → latin-1 → cp1252) because raw data has mixed encodings. This is non-negotiable for data integrity.

### Data Cleaning Rules
- Product names: remove embedded commas (e.g., "Mouse,Wireless" → "MouseWireless")
- Numeric fields: strip commas before type conversion (e.g., "1,916" → 1916)
- Skip lines with wrong field count (expect exactly 8 fields)

### ID Format Constraints
Validation checks prefix match (T/P/C) before ID usage. Do NOT bypass these—they prevent upstream data quality issues. Invalid records counted and reported in summary.

### Report Generation
- **Basic Report** (`report.txt`): Total revenue + region breakdown
- **Full Report** (`sales_report.txt`): Timestamp-stamped multi-section analysis with daily trends, top customers/products, performance metrics
- Always use Indian Rupee formatting (₹) and comma separators in output

## Key Files & Responsibilities

| File | Purpose |
|------|---------|
| [main.py](main.py) | Orchestrates pipeline; calls all utilities; generates both report formats |
| [utils/file_handler.py](utils/file_handler.py) | Multi-encoding file reading; skips header/empty lines |
| [utils/data_processor.py](utils/data_processor.py) | Parsing, validation, filtering; region/product/customer analytics |
| [utils/api_handler.py](utils/api_handler.py) | Local category lookup; external API fetch; transaction enrichment |
| [data/sales_data.txt](data/sales_data.txt) | Raw input (82 lines, mixed quality) |
| [output/report.txt](output/report.txt) | Basic summary (auto-generated) |
| [output/sales_report.txt](output/sales_report.txt) | Full analytics report (auto-generated) |

## Extension Points

- **Add Filters**: Extend `validate_and_filter()` parameters (e.g., date ranges, product categories)
- **Custom Enrichment**: Modify `enrich_sales_data()` to fetch from different APIs or add new fields
- **Report Formats**: Create new report functions mirroring `generate_sales_report()` pattern (build lines list → write with formatting)
- **Data Sources**: Replace file reading with DB queries by modifying [file_handler.py](utils/file_handler.py) input logic

## Common Tasks

### Run Full Pipeline
```bash
python main.py  # Validates, enriches, generates both reports
```

### Debug Invalid Records
Check `summary` dict returned by `validate_and_filter()` for counts. Add logging in validation loop to see which records fail and why.

### Add New Report Section
1. Aggregate data using `defaultdict` (see daily trends pattern in main.py)
2. Format as lines list with consistent section headers (`"="*44`, section name, `"-"*44`)
3. Append to report file with `f-string` formatting and Unicode symbols (₹)

### Extend Validation Rules
New rules go in `validate_and_filter()` validation loop. Update invalid count and return in summary for transparency.

## Performance Notes
- Dataset: ~82 raw records, ~70-71 valid after validation
- API Enrichment: Batches 100 products from DummyJSON; no caching (refetch each run)
- Report: O(n) aggregations using `defaultdict`; no database queries