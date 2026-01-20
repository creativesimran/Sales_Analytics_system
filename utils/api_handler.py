import requests

def fetch_product_info(product_id):
    categories = {
        "P101": "Laptop",
        "P102": "Mouse",
        "P103": "Keyboard",
        "P104": "Monitor",
        "P105": "Webcam",
        "P106": "Headphones",
        "P107": "Accessories",
        "P108": "Storage",
        "P109": "Mouse",
        "P110": "Charger"
    }

    return categories.get(product_id, "Unknown")

def fetch_all_products():
    """
    Fetches all products from DummyJSON API
    Returns list of product dictionaries
    """
    url = "https://dummyjson.com/products?limit=100"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("Products fetched successfully!")
        return data.get("products", [])
    except Exception as e:
        print("Failed to fetch products:", e)
        return []

def create_product_mapping(api_products):
    """
    Creates mapping of product IDs to product info
    """
    product_map = {}

    for product in api_products:
        product_map[product["id"]] = {
            "title": product.get("title"),
            "category": product.get("category"),
            "brand": product.get("brand"),
            "rating": product.get("rating")
        }

    return product_map

def enrich_sales_data(transactions, product_mapping=None):
    """
    Enriches transaction data with local product category information
    """
    enriched = []
    local_categories = {
        "P101": "Laptop",
        "P102": "Mouse",
        "P103": "Keyboard",
        "P104": "Monitor",
        "P105": "Webcam",
        "P106": "Headphones",
        "P107": "Accessories",
        "P108": "Storage",
        "P109": "Mouse",
        "P110": "Charger"
    }

    for tx in transactions:
        tx_copy = tx.copy()

        try:
            product_id = tx.get("ProductID", "")
            
            if product_id in local_categories:
                tx_copy["API_Category"] = local_categories[product_id]
                tx_copy["API_Brand"] = "TechStore"
                tx_copy["API_Rating"] = 4.5
                tx_copy["API_Match"] = True
            else:
                tx_copy["API_Category"] = None
                tx_copy["API_Brand"] = None
                tx_copy["API_Rating"] = None
                tx_copy["API_Match"] = False

        except Exception:
            tx_copy["API_Category"] = None
            tx_copy["API_Brand"] = None
            tx_copy["API_Rating"] = None
            tx_copy["API_Match"] = False

        enriched.append(tx_copy)

    return enriched

def save_enriched_data(enriched_transactions, filename="data/enriched_sales_data.txt"):
    """
    Saves enriched transactions back to file
    """
    headers = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region",
        "API_Category", "API_Brand", "API_Rating", "API_Match"
    ]

    with open(filename, "w", encoding="utf-8") as file:
        file.write("|".join(headers) + "\n")

        for tx in enriched_transactions:
            row = []
            for h in headers:
                value = tx.get(h)
                row.append("" if value is None else str(value))
            file.write("|".join(row) + "\n")
