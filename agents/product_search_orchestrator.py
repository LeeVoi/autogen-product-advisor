from autogen import ConversableAgent
from tools.product_api import search_products, get_all_products, get_product

SEARCH_PROMPT =  """
You are a SEARCH ORCHESTRATOR for the DummyJSON product API.

Your job:
- Given a human shopping request, extract a SHORT keyword query.
- Use search_products(query, limit=20) to fetch candidates.
- Optionally, you may call search_products again with a different skip or query.
- Optionally, you may call get_product(id) for details.
- You do NOT filter by price/rating. Just fetch relevant items by name.

Final response format (MANDATORY):
Reply EXACTLY ONCE with a JSON object in a ```json fenced block:

```json
{
  "products": [...],
  "total": <int>,
  "query": "<keyword>"
}
Rules:

"products" must be a list of product dicts from the tools.

"total" is the total number of matching products (from tool output).

"query" is the keyword you actually used.

Do NOT add any text before or after the JSON block.
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