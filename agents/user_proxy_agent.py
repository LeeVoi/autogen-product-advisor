from autogen import UserProxyAgent

def get_user_proxy() -> UserProxyAgent:
    """
    UserProxy is the HUMAN INTERFACE.
    
    - human_input_mode="ALWAYS": waits for user to type queries
    - llm_config=False: this agent does NOT call the LLM (it's the human)
    - It receives user input and passes it to ProductExpertAgent
    - It displays final results
    
    No tools registered here - the user just types and reads results.
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
        code_execution_config=False,
        system_message="""
        You are a helpful shopping assistant interface.
        When you receive product recommendations, acknowledge them.
        When you want to search, clearly state what you're looking for.
        """
    )
    
    return user_proxy