from typing import List, Dict, Any
import statistics


def score_product(product: Dict[str, Any]) -> float:
    """
    Compute a score used for ranking products.
    Formula combines rating, price, discount.
    """
    rating = product.get("rating", 0) or 0
    price = product.get("price", 1) or 1  # prevent divide-by-zero
    discount = product.get("discountPercentage", 0) or 0

    score = (rating * 2) + (discount / 5) - (price / 20)
    return round(score, 3)


def filter_by_price(products: List[Dict], max_price: float) -> List[Dict]:
    """Return products priced below or equal to max_price."""
    return [p for p in products if p.get("price", float("inf")) <= max_price]


def filter_by_rating(products: List[Dict], min_rating: float) -> List[Dict]:
    """Return products rated above or equal to min_rating."""
    return [p for p in products if p.get("rating", 0) >= min_rating]


def filter_by_category(products: List[Dict], category: str) -> List[Dict]:
    """Return products matching a specific category."""
    return [p for p in products if p.get("category", "").lower() == category.lower()]


def filter_by_availability(products: List[Dict], status: str = "In Stock") -> List[Dict]:
    """Return products matching the availability status."""
    return [p for p in products if p.get("availabilityStatus", "").lower() == status.lower()]


def filter_by_tags(products: List[Dict], tag: str) -> List[Dict]:
    """Return products containing a specific tag."""
    return [p for p in products if tag.lower() in [t.lower() for t in p.get("tags", [])]]


def compute_review_stats(product: Dict[str, Any]) -> Dict[str, float]:
    """
    Compute average review rating and return count.
    """
    reviews = product.get("reviews", [])
    if not reviews:
        return {"avg_review_rating": 0, "review_count": 0}

    ratings = [r.get("rating", 0) for r in reviews]
    avg_rating = statistics.mean(ratings) if ratings else 0

    return {
        "avg_review_rating": round(avg_rating, 2),
        "review_count": len(reviews),
    }


def compare_products(p1: Dict[str, Any], p2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare price, rating, score, discount between two products.
    Returns a summary dictionary.
    """
    return {
        "product_1": {
            "title": p1.get("title"),
            "price": p1.get("price"),
            "rating": p1.get("rating"),
            "discount": p1.get("discountPercentage"),
            "score": score_product(p1),
        },
        "product_2": {
            "title": p2.get("title"),
            "price": p2.get("price"),
            "rating": p2.get("rating"),
            "discount": p2.get("discountPercentage"),
            "score": score_product(p2),
        },
    }
