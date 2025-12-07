from autogen import AssistantAgent

CRITIC_PROMPT = """
You are an INTERNAL CRITIC for product recommendations.

You receive:
- The user's original request.
- The ProductAnalyzerAgent's recommendations.

Your job:
- Check if recommendations roughly match the user's constraints (type, budget, quality).
- Check that the reasoning is honest and not obviously made-up.
- Check clarity and usefulness.

Respond with one of:

APPROVED:
<short explanation of why this answer is acceptable>

or

REJECTED:
<short explanation of the problems and how to improve>
"""

def get_product_internal_critic_agent(custom_llm_config: dict) -> AssistantAgent:
    return AssistantAgent(
        name="ProductInternalCriticAgent",
        llm_config=custom_llm_config,
        system_message=CRITIC_PROMPT,
        human_input_mode="NEVER",
    )