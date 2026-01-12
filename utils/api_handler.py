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


