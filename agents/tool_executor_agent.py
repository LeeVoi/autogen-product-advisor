from autogen import UserProxyAgent

from tools.product_api import (
    search_products,
    get_all_products,
    get_product,
)


def get_tool_executor() -> UserProxyAgent:
    """
    Tool Executor Agent - "The Hands"
    
    This agent automatically executes tools suggested by other agents.
    
    Responsibilities:
    - Execute search_products, get_all_products, get_product (SearchOrchestrator)
    - Execute filter_by_price, filter_by_rating, score_product, compute_review_stats (ProductAnalyzerAgent)
    - Return results back to the requesting agent
    
    Configuration:
    - human_input_mode="NEVER": No human input, fully automated
    - llm_config=False: Not an LLM agent, just a tool executor
    - code_execution_config=False: Only execute registered tools, no arbitrary code
    - max_consecutive_auto_reply=10: Can execute multiple tools in sequence
    """

    tool_executor = UserProxyAgent(
        name="tool_executor",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        llm_config=False,
        code_execution_config=False,
        system_message="""
You are a tool executor. Your job is to:
1. Listen to agent requests
2. Execute the tools they ask for
3. Return the results immediately
4. Do not make decisions or analyze - just execute and return

Available tools: search_products, get_all_products, get_product, filter_by_price, filter_by_rating, score_product, compute_review_stats
"""
    )

    # --- Product API tools used by SearchOrchestrator ---
    tool_executor.register_for_execution(name="search_products")(search_products)
    tool_executor.register_for_execution(name="get_all_products")(get_all_products)
    tool_executor.register_for_execution(name="get_product")(get_product)

    return tool_executor