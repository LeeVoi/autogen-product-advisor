import json
import re
from typing import List, Dict, Any


def extract_json_block(text: str) -> str:
    """Extract the JSON payload from a ```json ... ``` fenced block."""
    if not text:
        return ""
    fence = re.search(r"```json\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    # fallback: any fenced block
    any_fence = re.search(r"```\s*([\s\S]*?)```", text)
    if any_fence:
        return any_fence.group(1).strip()
    return text.strip()


def parse_products_from_search(text: str) -> List[Dict[str, Any]]:
    """
    Parse the SearchOrchestrator's response into a list of product dicts.
    """
    raw = extract_json_block(text)
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except Exception:
        return []
    products = data.get("products") or []
    if not isinstance(products, list):
        return []
    return products


def format_products_for_analyzer(products: List[Dict[str, Any]], max_items: int = 15) -> str:
    """
    Create a compact textual list of products for the analyzer.
    """
    lines = []
    for i, p in enumerate(products[:max_items], start=1):
        title = p.get("title", "Unknown")
        brand = p.get("brand", "Unknown")
        price = p.get("price", "Unknown")
        rating = p.get("rating", "Unknown")
        lines.append(
            f"{i}) {title} | Brand: {brand} | Price: {price} | Rating: {rating}"
        )
    return "\n".join(lines)


def create_analyzer_prompt(user_request: str, products_text: str) -> str:
    return (
        "USER REQUEST:\n"
        f"{user_request}\n\n"
        "CANDIDATE PRODUCTS:\n"
        f"{products_text}\n\n"
        "Based on the above, recommend 2–3 products following your output format."
    )
