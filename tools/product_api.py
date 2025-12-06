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
    data = res.json()
    
    # Clean up the response - remove unnecessary fields for analysis
    cleaned_products = []
    for product in data.get('products', []):
        cleaned_products.append({
            'id': product['id'],
            'title': product['title'],
            'price': product['price'],
            'rating': product['rating'],
            'description': product['description'],
            'category': product['category'],
            'brand': product['brand'],
            'stock': product['stock'],
            'discountPercentage': product.get('discountPercentage', 0),
            'availabilityStatus': product['availabilityStatus'],
            'reviews_count': len(product.get('reviews', []))
        })
    
    return {
        'products': cleaned_products,
        'total': data['total'],
        'query': query
    }


def get_all_products(limit: int = 30, skip: int = 0) -> dict:
    """
    Fetch all products using pagination.
    Returns a dict with products list and total count.
    """
    all_products = []
    current_skip = skip
    
    while True:
        url = f"{BASE_URL}?limit={limit}&skip={current_skip}"
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        
        products = data.get('products', [])
        if not products:
            break
        
        for product in products:
            all_products.append({
                'id': product['id'],
                'title': product['title'],
                'price': product['price'],
                'rating': product['rating'],
                'description': product['description'],
                'category': product['category'],
                'brand': product['brand'],
                'stock': product['stock'],
                'discountPercentage': product.get('discountPercentage', 0),
                'availabilityStatus': product['availabilityStatus'],
                'reviews_count': len(product.get('reviews', []))
            })
        
        current_skip += limit
        
        if current_skip >= data.get('total', 0):
            break
    
    return {
        'products': all_products,
        'total': len(all_products)
    }