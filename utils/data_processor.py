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
        if not tx["CustomerID"].startswith("C"):
            invalid_count += 1
            continue
        if tx["Quantity"] <= 0 or tx["UnitPrice"] <= 0:
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


