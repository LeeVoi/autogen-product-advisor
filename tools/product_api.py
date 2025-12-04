import requests

BASE_URL = "https://dummyjson.com/products"


def get_product(product_id: int) -> dict:
    """
    Fetch a single product by ID.
    Returns a dict or raises an exception on failure.
    """
    url = f"{BASE_URL}/{product_id}"
    res = requests.get(url)

    res.raise_for_status()
    return res.json()


def search_products(query: str, limit: int = 30, skip: int = 0) -> dict:
    """
    Search for products based on a query string.
    Supports pagination via limit + skip.
    Returns a dict with 'products' list and 'total'.
    """
    url = f"{BASE_URL}/search?q={query}&limit={limit}&skip={skip}"
    res = requests.get(url)

    res.raise_for_status()
    return res.json()


def get_all_products(limit: int = 30) -> list:
    """
    Fetch all products using pagination.
    Returns a list of product dicts.
    """
    all_products = []
    skip = 0

    while True:
        url = f"{BASE_URL}?limit={limit}&skip={skip}"
        res = requests.get(url)
        res.raise_for_status()

        data = res.json()
        products = data.get("products", [])
        all_products.extend(products)

        # Stop when less than limit products are returned
        if len(products) < limit:
            break

        skip += limit

    return all_products
