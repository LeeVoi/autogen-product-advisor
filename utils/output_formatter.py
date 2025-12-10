import json
import re
from typing import List, Dict, Any


def extract_json_block(text: str) -> str:
    """
    Extract the JSON payload from a ```json ... ``` fenced block.

    Priority:
    1. Look for a ```json ... ``` block.
    2. If not found, look for any ``` ... ``` block.
    3. If still nothing, just return the raw text stripped.
    """
    if not text:
        return "" # Return empty string if no content
    
    # First, specifically look for a fenced block annotated with "json"
    # [\s\S]*? means "any characters including newlines, non-greedy"
    fence = re.search(r"```json\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    # fallback: any fenced block
    any_fence = re.search(r"```\s*([\s\S]*?)```", text)
    if any_fence:
        return any_fence.group(1).strip()
    # Final fallback: no fences at all, just return the stripped raw text
    return text.strip()


def parse_products_from_search(text: str) -> List[Dict[str, Any]]:
    """
    Parse the SearchOrchestrator's response into a list of product dicts.

    The SearchOrchestrator is expected to output something like:
    {
        "products": [
            {"title": "...", "brand": "...", ...},
            ...
        ]
    }

    This function:
    1. Extracts the JSON block from the LLM output.
    2. Parses it as JSON.
    3. Returns the "products" list or [] if anything fails.

    - perameters:
        - text: The full text response from the SearchOrchestrator agent.
        - returns: A list of product dictionaries extracted from the response.
    """

    # Try to extract just the JSON part from the LLM message
    raw = extract_json_block(text)
    if not raw:
        return [] # Return empty list if no content 
    try:
         # Convert JSON string → Python dict
        data = json.loads(raw)
    except Exception:
        # If JSON is invalid, fail gracefully with an empty list
        return []
    # Get "products" key, default to [] if missing or falsy
    products = data.get("products") or []
    # Ensure it's actually a list; if not, return empty list for safety
    if not isinstance(products, list):
        return []
    return products


def format_products_for_analyzer(products: List[Dict[str, Any]], max_items: int = 15) -> str:
    """
    Turn a list of product dicts into a compact text list for the analyzer agent.

    Example output:
    1) Product Name | Brand: X | Price: 100 USD | Rating: 4.5
    2) ...

    - We intentionally keep this format simple and consistent so the analyzer can easily read and reason over it.
    - A max_items parameter limits how many products to include (default 15, to avoid overwhelming the analyzer agent).
    """

    lines = []
    # Iterate over at most `max_items` products, numbering them starting from 1
    for i, p in enumerate(products[:max_items], start=1):
        # Get common fields; fall back to "Unknown" if missing
        title = p.get("title", "Unknown")
        brand = p.get("brand", "Unknown")
        price = p.get("price", "Unknown")
        rating = p.get("rating", "Unknown")
        # Build a single-line summary of the product
        lines.append(
            f"{i}) {title} | Brand: {brand} | Price: {price} | Rating: {rating}"
        )
    # Join all product lines into a single string separated by newlines
    return "\n".join(lines)


def create_analyzer_prompt(user_request: str, products_text: str) -> str:
    """
    Build the final prompt that will be sent to the Analyzer agent.

    It includes:
    - The original user request.
    - The formatted candidate products (this function will receive a max of 15 items which we call candidates).
    - Candidate products are formatted simply as a numbered list from the format_products_for_analyzer function.
    - A final instruction telling the analyzer what to do.
    """
    return (
        "USER REQUEST:\n"
        f"{user_request}\n\n"
        "CANDIDATE PRODUCTS:\n"
        f"{products_text}\n\n"
        "Based on the above, recommend 2–3 products following your output format."
    )
