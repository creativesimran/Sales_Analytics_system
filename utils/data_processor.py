def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries
    """

    transactions = []

    for line in raw_lines:
        parts = line.split("|")

        if len(parts) != 8:
            continue

        (
            transaction_id,
            date,
            product_id,
            product_name,
            quantity,
            unit_price,
            customer_id,
            region
        ) = parts

        product_name = product_name.replace(",", "")

        try:
            quantity = int(quantity.replace(",", ""))
            unit_price = float(unit_price.replace(",", ""))
        except ValueError:
            continue

        transactions.append({
            "TransactionID": transaction_id,
            "Date": date,
            "ProductID": product_id,
            "ProductName": product_name,
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "CustomerID": customer_id,
            "Region": region
        })

    return transactions


def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters
    """

    valid_transactions = []
    invalid_count = 0

    for tx in transactions:
        if not tx["TransactionID"].startswith("T"):
            invalid_count += 1
            continue
        if not tx["ProductID"].startswith("P"):
            invalid_count += 1
            continue
        if not tx["CustomerID"] or not tx["CustomerID"].startswith("C"):
            invalid_count += 1
            continue
        if tx["Quantity"] <= 0 or tx["UnitPrice"] <= 0:
            invalid_count += 1
            continue
        if not tx["Region"] or tx["Region"] not in ["North", "South", "East", "West"]:
            invalid_count += 1
            continue

        amount = tx["Quantity"] * tx["UnitPrice"]

        if region and tx["Region"] != region:
            continue
        if min_amount and amount < min_amount:
            continue
        if max_amount and amount > max_amount:
            continue

        valid_transactions.append(tx)

    summary = {
        "total_input": len(transactions),
        "invalid": invalid_count,
        "final_count": len(valid_transactions)
    }

    return valid_transactions, invalid_count, summary

def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions
    Returns: float
    """

    total_revenue = 0.0

    for tx in transactions:
        total_revenue += tx["Quantity"] * tx["UnitPrice"]

    return total_revenue

def region_wise_sales(transactions):
    """
    Analyzes sales by region
    Returns: dictionary with region statistics
    """

    region_data = {}
    total_sales = 0

    # First pass: calculate totals
    for tx in transactions:
        region = tx["Region"]
        amount = tx["Quantity"] * tx["UnitPrice"]
        total_sales += amount

        if region not in region_data:
            region_data[region] = {
                "total_sales": 0,
                "transaction_count": 0
            }

        region_data[region]["total_sales"] += amount
        region_data[region]["transaction_count"] += 1

    # Second pass: calculate percentage
    for region in region_data:
        region_data[region]["percentage"] = round(
            (region_data[region]["total_sales"] / total_sales) * 100, 2
        )

    # Sort by total_sales (descending)
    sorted_data = dict(
        sorted(
            region_data.items(),
            key=lambda x: x[1]["total_sales"],
            reverse=True
        )
    )

    return sorted_data

def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold
    Returns: list of tuples
    """

    product_data = {}

    for tx in transactions:
        name = tx["ProductName"]
        quantity = tx["Quantity"]
        revenue = quantity * tx["UnitPrice"]

        if name not in product_data:
            product_data[name] = {
                "quantity": 0,
                "revenue": 0
            }

        product_data[name]["quantity"] += quantity
        product_data[name]["revenue"] += revenue

    # Convert to list of tuples
    result = [
        (name, data["quantity"], data["revenue"])
        for name, data in product_data.items()
    ]

    # Sort by quantity sold (descending)
    result.sort(key=lambda x: x[1], reverse=True)

    return result[:n]

def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns
    Returns: dictionary of customer statistics
    """

    customers = {}

    for tx in transactions:
        cid = tx["CustomerID"]
        amount = tx["Quantity"] * tx["UnitPrice"]
        product = tx["ProductName"]

        if cid not in customers:
            customers[cid] = {
                "total_spent": 0,
                "purchase_count": 0,
                "products_bought": set()
            }

        customers[cid]["total_spent"] += amount
        customers[cid]["purchase_count"] += 1
        customers[cid]["products_bought"].add(product)

    # Final formatting
    for cid in customers:
        customers[cid]["avg_order_value"] = round(
            customers[cid]["total_spent"] / customers[cid]["purchase_count"], 2
        )
        customers[cid]["products_bought"] = list(customers[cid]["products_bought"])

    # Sort by total_spent (descending)
    sorted_customers = dict(
        sorted(
            customers.items(),
            key=lambda x: x[1]["total_spent"],
            reverse=True
        )
    )

    return sorted_customers

def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date
    Returns dictionary sorted by date
    """

    daily_data = {}

    for tx in transactions:
        date = tx["Date"]
        amount = tx["Quantity"] * tx["UnitPrice"]
        customer = tx["CustomerID"]

        if date not in daily_data:
            daily_data[date] = {
                "revenue": 0,
                "transaction_count": 0,
                "unique_customers": set()
            }

        daily_data[date]["revenue"] += amount
        daily_data[date]["transaction_count"] += 1
        daily_data[date]["unique_customers"].add(customer)

    # Convert set to count
    for date in daily_data:
        daily_data[date]["unique_customers"] = len(
            daily_data[date]["unique_customers"]
        )

    # Sort chronologically by date
    sorted_daily = dict(sorted(daily_data.items()))

    return sorted_daily

def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue
    Returns tuple (date, revenue, transaction_count)
    """

    daily_summary = {}

    for tx in transactions:
        date = tx["Date"]
        amount = tx["Quantity"] * tx["UnitPrice"]

        if date not in daily_summary:
            daily_summary[date] = {
                "revenue": 0,
                "transaction_count": 0
            }

        daily_summary[date]["revenue"] += amount
        daily_summary[date]["transaction_count"] += 1

    # Find peak day
    peak_date = max(
        daily_summary.items(),
        key=lambda x: x[1]["revenue"]
    )

    return (
        peak_date[0],
        peak_date[1]["revenue"],
        peak_date[1]["transaction_count"]
    )

def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales
    Returns list of tuples
    (ProductName, TotalQuantity, TotalRevenue)
    """

    product_data = {}

    # Aggregate quantity and revenue per product
    for tx in transactions:
        name = tx["ProductName"]
        quantity = tx["Quantity"]
        revenue = quantity * tx["UnitPrice"]

        if name not in product_data:
            product_data[name] = {
                "quantity": 0,
                "revenue": 0
            }

        product_data[name]["quantity"] += quantity
        product_data[name]["revenue"] += revenue

    # Filter low-performing products
    low_products = [
        (name, data["quantity"], data["revenue"])
        for name, data in product_data.items()
        if data["quantity"] < threshold
    ]

    # Sort by total quantity ascending
    low_products.sort(key=lambda x: x[1])

    return low_products
