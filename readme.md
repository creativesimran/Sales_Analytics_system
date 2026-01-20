# Sales Analytics System

## Overview
This project is a Python-based Sales Analytics System that reads raw sales data,
handles encoding issues, cleans and validates transactions, and generates
a region-wise sales report.

## Project Structure
- main.py – Main execution file
- utils/file_handler.py – File reading with encoding handling
- utils/data_processor.py – Parsing, cleaning, validation & filtering
- utils/api_handler.py – Product category lookup
- data/sales_data.txt – Raw sales data
- reports/report.txt – Final generated report

## Data Cleaning & Validation Rules
- Skips header and empty lines
- Handles non-UTF encodings (utf-8, latin-1, cp1252)
- Removes commas from product names and numeric values
- Converts Quantity to int and UnitPrice to float
- Removes invalid records:
  - Invalid TransactionID
  - Invalid ProductID or CustomerID
  - Quantity ≤ 0 or UnitPrice ≤ 0
- Applies optional filters (region and transaction amount)

## How to Run
```bash
python main.py

