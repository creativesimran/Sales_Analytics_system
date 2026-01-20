import os
from datetime import datetime
from collections import defaultdict

from utils.file_handler import read_sales_data
from utils.data_processor import parse_transactions, validate_and_filter
from utils.api_handler import fetch_product_info, fetch_all_products, create_product_mapping, enrich_sales_data, save_enriched_data

# ================= CONSTANTS =================
DATA_FILE = "data/sales_data.txt"
OUTPUT_DIR = "output"
BASIC_REPORT_FILE = os.path.join(OUTPUT_DIR, "report.txt")
FULL_REPORT_FILE = os.path.join(OUTPUT_DIR, "sales_report.txt")


# ================= BASIC REPORT =================
def generate_report(transactions):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total_revenue = 0
    region_sales = {}

    for tx in transactions:
        amount = tx["Quantity"] * tx["UnitPrice"]
        total_revenue += amount

        region = tx["Region"]
        region_sales[region] = region_sales.get(region, 0) + amount

    with open(BASIC_REPORT_FILE, "w", encoding="utf-8") as file:
        file.write(f"Total Revenue: {total_revenue}\n\n")
        file.write("Sales by Region:\n")
        for region, sales in region_sales.items():
            file.write(f"{region}: {sales}\n")

    print("✔ Basic report generated successfully!")


# ================= FULL SALES REPORT =================
def generate_sales_report(transactions, enriched_transactions, output_file=FULL_REPORT_FILE):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    lines = []

    # -------- HEADER --------
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.extend([
        "=" * 44,
        "           SALES ANALYTICS REPORT",
        f"Generated: {now}",
        f"Records Processed: {len(transactions)}",
        "=" * 44,
        ""
    ])

    # -------- OVERALL SUMMARY --------
    total_revenue = sum(t["Quantity"] * t["UnitPrice"] for t in transactions)
    avg_order_value = total_revenue / len(transactions) if transactions else 0

    dates = sorted(t["Date"] for t in transactions)
    date_range = f"{dates[0]} to {dates[-1]}" if dates else "N/A"

    lines.extend([
        "OVERALL SUMMARY",
        "-" * 44,
        f"Total Revenue:        ₹{total_revenue:,.2f}",
        f"Total Transactions:   {len(transactions)}",
        f"Average Order Value:  ₹{avg_order_value:,.2f}",
        f"Date Range:           {date_range}",
        ""
    ])

    # -------- REGION PERFORMANCE --------
    region_sales = defaultdict(float)
    region_count = defaultdict(int)

    for t in transactions:
        amt = t["Quantity"] * t["UnitPrice"]
        region_sales[t["Region"]] += amt
        region_count[t["Region"]] += 1

    lines.append("REGION-WISE PERFORMANCE")
    lines.append("-" * 44)
    lines.append(f"{'Region':<10}{'Sales':<15}{'% of Total':<12}{'Transactions'}")

    for region, sales in sorted(region_sales.items(), key=lambda x: x[1], reverse=True):
        percent = (sales / total_revenue) * 100 if total_revenue else 0
        lines.append(f"{region:<10}₹{sales:<14,.0f}{percent:<12.2f}{region_count[region]}")

    lines.append("")

    # -------- TOP 5 PRODUCTS --------
    product_qty = defaultdict(int)
    product_rev = defaultdict(float)

    for t in transactions:
        product_qty[t["ProductName"]] += t["Quantity"]
        product_rev[t["ProductName"]] += t["Quantity"] * t["UnitPrice"]

    lines.append("TOP 5 PRODUCTS")
    lines.append("-" * 44)
    lines.append(f"{'Rank':<6}{'Product':<20}{'Qty':<8}{'Revenue'}")

    for i, (p, q) in enumerate(sorted(product_qty.items(), key=lambda x: x[1], reverse=True)[:5], 1):
        lines.append(f"{i:<6}{p:<20}{q:<8}₹{product_rev[p]:,.0f}")

    lines.append("")

    # -------- TOP 5 CUSTOMERS --------
    customer_spend = defaultdict(float)
    customer_orders = defaultdict(int)

    for t in transactions:
        amt = t["Quantity"] * t["UnitPrice"]
        customer_spend[t["CustomerID"]] += amt
        customer_orders[t["CustomerID"]] += 1

    lines.append("TOP 5 CUSTOMERS")
    lines.append("-" * 44)
    lines.append(f"{'Rank':<6}{'Customer':<12}{'Spent':<15}{'Orders'}")

    for i, (c, s) in enumerate(sorted(customer_spend.items(), key=lambda x: x[1], reverse=True)[:5], 1):
        lines.append(f"{i:<6}{c:<12}₹{s:<14,.0f}{customer_orders[c]}")

    lines.append("")

    # -------- DAILY SALES TREND --------
    daily_rev = defaultdict(float)
    daily_customers = defaultdict(set)

    for t in transactions:
        amt = t["Quantity"] * t["UnitPrice"]
        daily_rev[t["Date"]] += amt
        daily_customers[t["Date"]].add(t["CustomerID"])

    lines.append("DAILY SALES TREND")
    lines.append("-" * 44)
    lines.append(f"{'Date':<12}{'Revenue':<15}{'Transactions':<15}{'Customers'}")

    for d in sorted(daily_rev):
        lines.append(f"{d:<12}₹{daily_rev[d]:<14,.0f}{len(daily_customers[d]):<15}{len(daily_customers[d])}")

    lines.append("")

    # -------- PRODUCT PERFORMANCE --------
    best_day = max(daily_rev.items(), key=lambda x: x[1])[0] if daily_rev else "N/A"
    low_products = [p for p, q in product_qty.items() if q < 10]

    lines.extend([
        "PRODUCT PERFORMANCE ANALYSIS",
        "-" * 44,
        f"Best Selling Day: {best_day}",
        f"Low Performing Products: {', '.join(low_products) if low_products else 'None'}",
        ""
    ])

    # -------- API ENRICHMENT SUMMARY --------
    enriched = [t for t in enriched_transactions if t.get("API_Match")]
    failed = [t["ProductID"] for t in enriched_transactions if not t.get("API_Match")]

    success_rate = (len(enriched) / len(enriched_transactions)) * 100 if enriched_transactions else 0

    lines.extend([
        "API ENRICHMENT SUMMARY",
        "-" * 44,
        f"Total Products Enriched: {len(enriched)}",
        f"Success Rate: {success_rate:.2f}%",
        f"Products Not Enriched: {', '.join(set(failed)) if failed else 'None'}"
    ])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("✔ Comprehensive sales report generated successfully!")


# ================= MAIN =================
def main():
    print("=" * 40)
    print("       SALES ANALYTICS SYSTEM")
    print("=" * 40)

    raw_lines = read_sales_data(DATA_FILE)
    transactions = parse_transactions(raw_lines)

    valid_data, invalid_count, summary = validate_and_filter(transactions)

    # Enrich data with local product information
    enriched_data = enrich_sales_data(valid_data)
    save_enriched_data(enriched_data)

    print("Summary:", summary)

    generate_report(valid_data)
    generate_sales_report(valid_data, enriched_data)

    print("\n✔ PROCESS COMPLETED SUCCESSFULLY")
    print("Reports generated in /output folder")


if __name__ == "__main__":
    main()
