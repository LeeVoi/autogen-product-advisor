from autogen import ConversableAgent
from tools.product_api import search_products, get_all_products, get_product

SEARCH_PROMPT = """
You are a SEARCH ORCHESTRATOR - API specialist.

Your ONLY job: Fetch product data from the API by KEYWORD/NAME SEARCH.

Important: The API does NOT support price filtering, rating filtering, etc.
You can ONLY search by product name/keyword.

Available tools:
- search_products(query) - search by keyword (phone, laptop, etc.)
- get_all_products(limit) - get all products
- get_product(id) - get specific product by ID

Simply fetch the raw data. The ANALYZER will handle all filtering by price, rating, availability, etc.

Return the raw product data you fetch. Nothing else.
"""

def get_search_orchestrator_agent(custom_llm_config: dict) -> ConversableAgent:
    agent = ConversableAgent(
        name="SearchOrchestrator",
        llm_config=custom_llm_config,
        system_message=SEARCH_PROMPT,
        human_input_mode="NEVER",
    )
    
    # Register ONLY for LLM (so it knows tools exist and can suggest them)
    # tool_executor will handle the actual execution
    agent.register_for_llm(
        name="search_products",
        description="Search for products by keyword query. Returns a list of products with id, title, price, rating, description, discount, availability status, and reviews."
    )(search_products)
    
    agent.register_for_llm(
        name="get_all_products",
        description="Get all available products with pagination. Parameters: limit (default 30), skip (default 0). Returns list of products."
    )(get_all_products)
    
    agent.register_for_llm(
        name="get_product",
        description="Get complete details for a specific product by its ID. Returns full product information including all metadata."
    )(get_product)
    
    return agent