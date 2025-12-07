from autogen import UserProxyAgent

from tools.product_api import (
    search_products,
    get_all_products,
    get_product,
)


def get_tool_executor() -> UserProxyAgent:
    tool_executor = UserProxyAgent(
        name="tool_executor",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        llm_config=False,
        code_execution_config=False,
        is_termination_msg=lambda msg: (
            isinstance(msg, dict)
            and isinstance(msg.get("content"), str)
            and "```json" in msg["content"]
        ),
        system_message="""
        You are a tool executor. Your job is to:
        1. Listen to agent requests
        2. Execute the tools they ask for
        3. Return the results immediately
        4. Do not make decisions or analyze - just execute and return
        """,
    )

    # Register product tools
    tool_executor.register_for_execution(name="search_products")(search_products)
    tool_executor.register_for_execution(name="get_all_products")(get_all_products)
    tool_executor.register_for_execution(name="get_product")(get_product)

    return tool_executor
