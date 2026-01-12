import os

from utils.file_handler import read_sales_data
from utils.data_processor import parse_transactions, validate_and_filter
from utils.api_handler import fetch_product_info

DATA_FILE = "data/sales_data.txt"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "report.txt")


def generate_report(transactions):
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    total_revenue = 0
    region_sales = {}

    for tx in transactions:
        amount = tx["Quantity"] * tx["UnitPrice"]
        total_revenue += amount

        region = tx["Region"]
        region_sales[region] = region_sales.get(region, 0) + amount

    with open(OUTPUT_FILE, "w") as file:
        file.write(f"Total Revenue: {total_revenue}\n\n")
        file.write("Sales by Region:\n")
        for region, sales in region_sales.items():
            file.write(f"{region}: {sales}\n")

    print("Report generated successfully!")


def main():
    raw_lines = read_sales_data(DATA_FILE)
    transactions = parse_transactions(raw_lines)

    valid_data, invalid_count, summary = validate_and_filter(transactions)

    for record in valid_data:
        record["Category"] = fetch_product_info(record["ProductID"])

    print("Summary:", summary)
    generate_report(valid_data)


if __name__ == "__main__":
    main()


