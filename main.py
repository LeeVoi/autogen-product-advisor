import logging
import json

from config.llm_config import LLM_CONFIG

from agents.product_search_orchestrator import get_search_orchestrator_agent
from agents.product_analyzer_agent import get_product_analyzer_agent
from agents.product_internal_critic_agent import get_product_internal_critic_agent
from agents.tool_executor_agent import get_tool_executor

from utils.output_formatter import extract_json_block, format_products_for_analyzer

logging.basicConfig(level=logging.INFO)


def get_last_message_from(chat, agent_name: str) -> str:
    """
    Helper to pull the last message from a specific agent
    in an Autogen ChatResult.
    (Currently not used, but kept in case you want it later.)
    """
    for msg in reversed(chat.chat_history):
        if msg.get("name") == agent_name:
            return msg.get("content") or ""
    return ""


def parse_products_from_search(raw_text: str):
    """
    Takes a reply that contains a JSON block and returns the 'products' list.
    """
    block = extract_json_block(raw_text)
    if not block:
        return []

    try:
        data = json.loads(block)
    except json.JSONDecodeError:
        return []

    products = data.get("products")
    if isinstance(products, list):
        return products
    return []


def print_banner():
    print("\n" + "=" * 70)
    print("PRODUCT ADVISOR - Interactive Assistant")
    print("=" * 70 + "\n")
    print("Type 'exit', 'quit', or 'q' to quit.\n")


def main():
    # --- Create agents ---
    search_agent = get_search_orchestrator_agent(custom_llm_config=LLM_CONFIG)
    analyzer_agent = get_product_analyzer_agent(custom_llm_config=LLM_CONFIG)
    critic_agent = get_product_internal_critic_agent(custom_llm_config=LLM_CONFIG)
    tool_executor = get_tool_executor()

    print_banner()

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit", "q"):
            print("\nGoodbye!\n")
            break

        if not user_input:
            continue

        try:
            # -------------------------------------------------
            # STEP 1: SEARCH (uses tools via tool_executor)
            # -------------------------------------------------
            print("\n" + "-" * 70)
            print("⏳ Processing your request...\n")
            print("[Searching] Finding products...\n")

            search_prompt = (
                "User wants:\n"
                f"{user_input}\n\n"
                "Use a good keyword, search for products, and return JSON as specified."
            )

            chat_search = tool_executor.initiate_chat(
                search_agent,
                message=search_prompt,
                max_turns=8,  # give orchestrator enough room to call tools & finish
            )

            # --- Look for the latest JSON-ish message with "products" from ANY agent ---
            search_text = ""
            for msg in reversed(chat_search.chat_history):
                content = msg.get("content") or ""
                if not content:
                    continue
                if '"products"' in content or '"products":' in content or '{\n  "products"' in content:
                    search_text = content
                    break

            if not search_text:
                print("⚠️ Could not find any JSON results from the search agent.\n")
                # Debug helper (uncomment if needed):
                # for m in chat_search.chat_history:
                #     print(m.get("name"), "=>", repr(m.get("content")))
                continue

            products = parse_products_from_search(search_text)

            if not products:
                print("⚠️ Could not parse any products from the search response.\n")
                print("Raw response:\n")
                print(search_text)
                print()
                continue

            # -------------------------------------------------
            # STEP 2: ANALYZE (direct LLM call, NO tool_executor)
            # -------------------------------------------------
            print("[Analyzing] Ranking products...\n")

            products_text = format_products_for_analyzer(products)
            analyzer_prompt = (
                "USER REQUEST:\n"
                f"{user_input}\n\n"
                "CANDIDATE PRODUCTS:\n"
                f"{products_text}\n\n"
                "Based on the above, recommend 2–3 products following your output format."
            )

            analyzer_msg = analyzer_agent.generate_reply(
                messages=[{"role": "user", "content": analyzer_prompt}]
            )
            analyzer_result = (
                analyzer_msg.get("content", "")
                if isinstance(analyzer_msg, dict)
                else str(analyzer_msg)
            )

            if not analyzer_result.strip():
                print("⚠️ Analyzer did not return any content.\n")
                continue

            # -------------------------------------------------
            # STEP 3: CRITIC (direct LLM call, NO tool_executor)
            # -------------------------------------------------
            print("[Critic] Reviewing recommendations...\n")

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

            # -------------------------------------------------
            # STEP 4: Print final result
            # -------------------------------------------------
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

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error occurred: {e}")
            import traceback
            traceback.print_exc()
            print("Please try another query.\n")


if __name__ == "__main__":
    main()
