import sqlite3
import random


def hybrid_recommendation(cart_products):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if not cart_products:
        return []

    # Get categories from cart
    categories = set()

    for p in cart_products:
        categories.add(p["category"])

    recommended = []

    # Get products from each category
    for cat in categories:

        cur.execute(
        "SELECT * FROM products WHERE category=? ORDER BY RANDOM() LIMIT 4",
        (cat,)
        )

        items = cur.fetchall()

        for item in items:
            recommended.append(item)

    # Remove duplicates
    unique_products = []
    seen = set()

    for product in recommended:

        if product["id"] not in seen:
            unique_products.append(product)
            seen.add(product["id"])

    # Shuffle for mix recommendation
    random.shuffle(unique_products)

    conn.close()

    return unique_products[:8]