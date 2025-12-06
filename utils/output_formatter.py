import json
import re
from typing import List, Dict, Any, Optional

def extract_json_block(text: str) -> str:
    if not text:
        return ""
    fence = re.search(r"```json\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    any_fence = re.search(r"```\s*([\s\S]*?)\s*```", text)
    if any_fence:
        return any_fence.group(1).strip()
    trimmed = text.strip()
    if trimmed.startswith("{") or trimmed.startswith("["):
        return trimmed
    return ""

def extract_largest_json(text: str) -> str:
    if not text:
        return ""
    best = ""
    # objects
    stack = []
    starts = []
    for i, ch in enumerate(text):
        if ch == "{":
            stack.append("{"); starts.append(i)
        elif ch == "}" and stack:
            stack.pop(); s = starts.pop()
            seg = text[s:i+1]
            try:
                json.loads(seg)
                if len(seg) > len(best): best = seg
            except: pass
    # arrays
    stack = []; starts = []
    for i, ch in enumerate(text):
        if ch == "[":
            stack.append("["); starts.append(i)
        elif ch == "]" and stack:
            stack.pop(); s = starts.pop()
            seg = text[s:i+1]
            try:
                json.loads(seg)
                if len(seg) > len(best): best = seg
            except: pass
    return best

def parse_json_safely(json_str: str) -> List[Dict[str, Any]]:
    candidate = extract_json_block(json_str) or extract_largest_json(json_str) or json_str
    def try_load(s) -> Optional[Any]:
        try:
            return json.loads(s)
        except Exception:
            return None
    data = try_load(candidate)
    if data is None:
        return []
    products: List[Dict[str, Any]] = []
    try:
        if isinstance(data, dict) and "search_products_response" in data:
            results = data["search_products_response"].get("results", [])
            if not results:
                return []
            first = results[0]
            if isinstance(first, str):
                inner = try_load(first) or {}
                products = inner.get("products", [])
            elif isinstance(first, dict):
                products = first.get("products", [])
        elif isinstance(data, dict) and "products" in data:
            products = data.get("products", [])
        elif isinstance(data, list):
            products = [p for p in data if isinstance(p, dict)]
    except Exception:
        return []
    clean = []
    for p in products:
        if not isinstance(p, dict):
            continue
        clean.append({
            "title": p.get("title", "Unknown"),
            "brand": p.get("brand", "Unknown"),
            "price": p.get("price", "N/A"),
            "rating": p.get("rating", "N/A"),
            "availabilityStatus": p.get("availabilityStatus", "Unknown"),
            "category": p.get("category", ""),
            "description": p.get("description", ""),
        })
    return clean

def format_products_for_analyzer(products: List[Dict[str, Any]]) -> str:
    if not products:
        return "No products found."
    lines = ["Available Products (compact):"]
    for i, p in enumerate(products[:12], 1):
        lines.append(
            f"{i}. {p['title']} — {p['brand']} | ${p['price']} | ⭐ {p['rating']}/5 | {p['availabilityStatus']}"
        )
    return "\n".join(lines)

def create_analyzer_prompt(user_request: str, products_text: str) -> str:
    return f"""Recommend exactly TOP 3 PRODUCTS for this request: "{user_request}"

Only pick from the list below. Only include items that fit the user's constraints.

{products_text}

Return ONLY the 3 recommendations in this exact structure:

PRODUCT #1
Name: <product name>
Brand: <brand>
Price: $<price>
Rating: <rating>/5
Why chosen: <2-3 sentences>
Strengths:
- <point>
- <point>
Limitations:
- <point>

PRODUCT #2
Name: <product name>
Brand: <brand>
Price: $<price>
Rating: <rating>/5
Why chosen: <2-3 sentences>
Strengths:
- <point>
- <point>
Limitations:
- <point>

PRODUCT #3
Name: <product name>
Brand: <brand>
Price: $<price>
Rating: <rating>/5
Why chosen: <2-3 sentences>
Strengths:
- <point>
- <point>
Limitations:
- <point>"""