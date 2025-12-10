from typing import List, Dict, Any
import statistics
import re

"""
NOTE: The functions in this file are no longer used by the analyzer
in the current implementation. The file is kept for reference and
for context as they are mentioned in the project report.

originally, this file contained helper functions for filtering, scoring, and comparing products.
These functions were registered as tools for the ProductAnalyzerAgent to help the agent if it chose to use them.

In the final version of the system, we simplified the analyzer flow
and removed this tool integration, but we kept the module to document
the earlier design.
"""

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


def parse_constraints(query: str) -> Dict[str, Any]:
    """
    Parse user query into constraints.
    Supports:
    - price_max: under/less than/<=/</around $X
    - rating_min: >= / at least / no less than X
    - category_in: smartphones/phones/mobile if mentioned
    - availability: in stock / out of stock / low stock
    - brand_in: simple list of known brands found in query
    - count: top N or 'N items/products/phones'
    """
    q = query.lower()
    constraints: Dict[str, Any] = {}

    # price_max
    m_price = re.search(r"(under|less than|<=|<|around)\s*\$?\s*(\d+(\.\d+)?)", q)
    if m_price:
        constraints["price_max"] = float(m_price.group(2))

    # rating_min
    m_rating_ge = re.search(r"(?:>=|at least|no less than)\s*(\d+(\.\d+)?)", q)
    if m_rating_ge:
        constraints["rating_min"] = float(m_rating_ge.group(1))
    else:
        m_rating_plain = re.search(r"rating\s*(?:>=|>|at least|no less than)?\s*(\d+(\.\d+)?)", q)
        if m_rating_plain:
            constraints["rating_min"] = float(m_rating_plain.group(1))

    # category_in
    if any(w in q for w in ("smartphone", "smartphones", "phone", "phones")):
        constraints["category_in"] = {"smartphones", "phones", "mobile"}

    # availability
    if "in stock" in q:
        constraints["availability"] = "in stock"
    elif "out of stock" in q:
        constraints["availability"] = "out of stock"
    elif "low stock" in q:
        constraints["availability"] = "low stock"

    # brand_in
    brands = ["apple", "samsung", "oppo", "realme", "vivo", "xiaomi", "oneplus", "google", "nokia", "motorola"]
    for b in brands:
        if b in q:
            constraints.setdefault("brand_in", set()).add(b.capitalize())

    # count
    m_count = re.search(r"(top\s*(\d+)|\b(\d+)\s*(items|products|phones))", q)
    if m_count:
        num = m_count.group(2) or m_count.group(3)
        if num and num.isdigit():
            constraints["count"] = int(num)

    return constraints


def filter_by_constraints(products: List[Dict[str, Any]], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filter products using parsed constraints."""
    def ok(p: Dict[str, Any]) -> bool:
        # price_max
        if "price_max" in constraints:
            try:
                if float(p.get("price", float("inf"))) > float(constraints["price_max"]):
                    return False
            except Exception:
                return False

        # rating_min
        if "rating_min" in constraints:
            try:
                if float(p.get("rating", 0)) < float(constraints["rating_min"]):
                    return False
            except Exception:
                return False

        # category_in
        if "category_in" in constraints:
            cat = (p.get("category") or "").lower()
            if cat not in constraints["category_in"]:
                return False

        # availability
        if "availability" in constraints:
            want = constraints["availability"].lower()
            avail = (p.get("availabilityStatus") or "").lower()
            if avail != want:
                return False

        # brand_in
        if "brand_in" in constraints:
            brand = (p.get("brand") or "")
            if brand.capitalize() not in constraints["brand_in"]:
                return False

        return True

    filtered = [p for p in products if ok(p)]

    # count
    count = constraints.get("count")
    if isinstance(count, int) and count > 0:
        filtered = filtered[:count]

    return filtered
