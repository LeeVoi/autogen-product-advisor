from autogen import UserProxyAgent

def get_user_proxy() -> UserProxyAgent:
    """
    UserProxy is the HUMAN INTERFACE.
    """
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=0,
        llm_config=False,
        is_termination_msg=lambda msg: (
            isinstance(msg, dict)
            and isinstance(msg.get("content"), str)
            and "TERMINATE" in msg["content"]
        ),
        code_execution_config=False,  # CRITICAL: Disable code execution on user_proxy
        system_message="""
You are a helpful shopping assistant interface.
When you receive product recommendations, acknowledge them.
When you want to search, clearly state what you're looking for.
"""
    )
    
    return user_proxy