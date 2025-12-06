from autogen import AssistantAgent

CRITIC_PROMPT = """
You are an INTERNAL CRITIC - Quality evaluator.

Your job: Review the Analyzer's recommendations.

Check:
✓ Are these products relevant to the user's request?
✓ Is the analysis sound and honest?
✓ Are there any obvious errors or missing data?
✓ Would you recommend these products?

Respond with:
APPROVED: [explanation]
OR
REJECTED: [what's wrong + suggestions]
"""

def get_product_internal_critic_agent(custom_llm_config: dict) -> AssistantAgent:
    return AssistantAgent(
        name="ProductInternalCriticAgent",
        llm_config=custom_llm_config,
        system_message=CRITIC_PROMPT,
        human_input_mode="NEVER",
    )