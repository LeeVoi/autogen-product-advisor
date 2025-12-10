import logging
import json
import warnings

from config.llm_config import LLM_CONFIG

from agents.product_search_orchestrator import get_search_orchestrator_agent
from agents.product_analyzer_agent import get_product_analyzer_agent
from agents.product_internal_critic_agent import get_product_internal_critic_agent
from agents.tool_executor_agent import get_tool_executor

from utils.output_formatter import extract_json_block, format_products_for_analyzer, parse_products_from_search

# Configure global logging levels for this script.
logging.basicConfig(level=logging.INFO)
# Suppress overly verbose logs from httpx and used internally by Autogen (HTTP client used by LLMs)
logging.getLogger("httpx").setLevel(logging.WARNING)
# Suppress pydantic warnings about future changes.
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="pydantic"
)

def print_banner():
    """
    Simple CLI banner shown when the program starts.
    """
    print("\n" + "=" * 70)
    print("PRODUCT ADVISOR - Interactive Assistant")
    print("=" * 70 + "\n")
    print("Type 'exit', 'quit', or 'q' to quit.\n")


def main():
    """
    Main entry point for the Product Advisor CLI application.

    High-level flow for each user query:
        1. Create the agents (search, analyzer, critic) and the tool executor.
        2. Read user input (e.g., "find me a phone under 200$").
        3. Use the tool executor + search orchestrator agent to:
            - Decide on search queries.
            - Call product APIs via tools.
            - Aggregate results into a JSON structure with "products".
        4. Extract and parse the products from the search result.
        5. Format those products into a compact text list for the analyzer.
        6. Call the analyzer agent directly (single LLM call) to:
            - Rank, compare, and pick 2–3 recommendations.
        7. Call the critic agent directly (single LLM call) to:
            - Review and critique the analyzer's recommendations.
        8. Print both the recommendations and the critic review to the user.
    """
    # Assign and create agents
    search_agent = get_search_orchestrator_agent(custom_llm_config=LLM_CONFIG)
    analyzer_agent = get_product_analyzer_agent(custom_llm_config=LLM_CONFIG)
    critic_agent = get_product_internal_critic_agent(custom_llm_config=LLM_CONFIG)
    tool_executor = get_tool_executor()

    print_banner()

    # Main interactive loop
    while True:
        user_input = input("You: ").strip() # Read user input
        if user_input.lower() in ("exit", "quit", "q"): # Exit commands
            print("\nGoodbye!\n")
            break
        
        # Skip empty inputs and ask again for a user input
        if not user_input:
            continue

        try:
         
            # Search phase, Multi-turn chat with tools.
     
            print("\n" + "-" * 70)
            print("⏳ Processing your request...\n")
            print("[Searching] Finding products...\n")

            # this prompt guides the orchestrator by telling it what to do.
            search_prompt = (
                "User wants:\n"
                f"{user_input}\n\n"
                "Use a good keyword, search for products, and return JSON as specified."
            )

            # tool_executor.initiate_chat handles the multi-turn chat with tool calls
            # - the orchestrator agent decides when/how to call tools
            # - the tool executor runs the tools and returns results
            chat_search = tool_executor.initiate_chat(
                search_agent,
                message=search_prompt,
                max_turns=8,  # give orchestrator enough room to call tools & finish
            )

            # After the multi-turn search conversation, we scan the chat history
            # from the end to find the last message that looks like it contains
            # a JSON object with a "products" field.
            search_text = ""
            for msg in reversed(chat_search.chat_history):
                content = msg.get("content") or ""
                if not content:
                    continue
                # Look for common patterns indicating a products JSON.
                if '"products"' in content or '"products":' in content or '{\n  "products"' in content:
                    search_text = content
                    break
            
            # If we couldn't find any JSON results, inform the user.
            # we cannot proceed further without products to analyze.
            if not search_text:
                print("⚠️ Could not find any JSON results from the search agent.\n")
                continue

            # Parse products from the extracted JSON text
            products = parse_products_from_search(search_text)

            # If no products were parsed or parsing failed, show debug info and restart.
            if not products:
                print("⚠️ Could not parse any products from the search response.\n")
                print("Raw response:\n")
                print(search_text)
                print()
                continue

            #Analyze contents, direct LLM call
            print("[Analyzing] Ranking products...\n")

            # Turn the list of product dicts into a compact, numbered text list.
            # This becomes the "candidate products" section for the analyzer.
            products_text = format_products_for_analyzer(products)

            # Build the full prompt for the analyzer agent:
            # - Include the original user request.
            # - Include the formatted candidate product list.
            # - Instruct the analyzer to recommend 2–3 products and follow
            #   its defined output format (described in its system prompt).
            analyzer_prompt = (
                "USER REQUEST:\n"
                f"{user_input}\n\n"
                "CANDIDATE PRODUCTS:\n"
                f"{products_text}\n\n"
                "Based on the above, recommend 2–3 products following your output format."
            )

            # Direct call to the analyzer agent (no tools here, pure LLM response).
            analyzer_msg = analyzer_agent.generate_reply(
                messages=[{"role": "user", "content": analyzer_prompt}]
            )

            # The return type can vary depending on the Autogen setup (dict/string),
            # so we normalize it to a string for printing and further use.
            analyzer_result = (
                analyzer_msg.get("content", "")
                if isinstance(analyzer_msg, dict)
                else str(analyzer_msg)
            )

            if not analyzer_result.strip():
                print("⚠️ Analyzer did not return any content.\n")
                continue

            #Critic grades contents also direct LLM call
            print("[Critic] Reviewing recommendations...\n")

            # Build the critic prompt including:
            # - The original user request.
            # - The analyzer's recommendations.
            critic_prompt = (
                "User request:\n"
                f"{user_input}\n\n"
                "Analyzer recommendations:\n"
                f"{analyzer_result}\n\n"
                "Evaluate them according to your system message."
            )

            critic_msg = critic_agent.generate_reply(
                messages=[{"role": "user", "content": critic_prompt}]
            )
            critic_result = (
                critic_msg.get("content", "")
                if isinstance(critic_msg, dict)
                else str(critic_msg)
            )

            # Display final results to the user
            print("\n" + "=" * 70)
            print("RECOMMENDED PRODUCTS")
            print("=" * 70 + "\n")
            print(analyzer_result.strip())

            print("\n" + "=" * 70)
            print("CRITIC REVIEW")
            print("=" * 70 + "\n")
            print(critic_result.strip() or "(No critic feedback)")

            print("\n" + "-" * 70)
            print("Ready for your next query.\n")

        # Handle user interrupt (Ctrl+C) gracefully.
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        # Catch-all error handling so the app does not crash
        except Exception as e:
            print(f"\n❌ Error occurred: {e}")
            import traceback
            traceback.print_exc()
            print("Please try another query.\n")


if __name__ == "__main__":
    main()
