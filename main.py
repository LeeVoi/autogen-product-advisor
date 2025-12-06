import logging
import sys
from io import StringIO

from config.llm_config import LLM_CONFIG
from agents.product_search_orchestrator import get_search_orchestrator_agent
from agents.product_analyzer_agent import get_product_analyzer_agent
from agents.tool_executor_agent import get_tool_executor
from utils.output_formatter import (
    parse_json_safely,
    format_products_for_analyzer,
    create_analyzer_prompt,
)

# Suppress ALL logging
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger("autogen").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)


def extract_message(chat_history, agent_name: str) -> str:
    """Return last non-empty message content from a specific agent."""
    for msg in reversed(chat_history):
        if msg.get("name") == agent_name:
            content = (msg.get("content") or "").strip()
            if content and len(content) > 20:
                return content
    return ""


def main():
    # Initialize agents quietly
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    search_orchestrator = get_search_orchestrator_agent(custom_llm_config=LLM_CONFIG)
    product_analyzer = get_product_analyzer_agent(custom_llm_config=LLM_CONFIG)
    tool_executor = get_tool_executor()
    sys.stdout = old_stdout

    print("\n" + "="*70)
    print("PRODUCT ADVISOR - Interactive Assistant")
    print("="*70)
    print("\nWelcome! I can help you find products matching your criteria.")
    print("\nExample queries:")
    print("  • Find me a phone around 200$ price")
    print("  • Find 3 laptops good for gaming and development, under 1000 EUR")
    print("  • I need a budget laptop under 500 EUR with 15+ inch screen")
    print("  • Show me gaming headphones with good reviews")
    print("\nType 'exit', 'quit', or 'q' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ("exit", "quit", "q"):
                print("\nThank you for using Product Advisor. Goodbye!")
                break
            if not user_input:
                continue

            print("\n" + "-"*70)
            print("⏳ Processing your request...\n")

            # Search (suppress stdout)
            sys_sav = sys.stdout
            sys.stdout = StringIO()
            chat_search = tool_executor.initiate_chat(
                search_orchestrator, message=user_input, max_turns=3
            )
            sys.stdout = sys_sav

            raw_search = extract_message(chat_search.chat_history, "SearchOrchestrator")

            # Temporary debug: write to file (no terminal spam)
            try:
                with open("search_debug.txt", "w", encoding="utf-8") as f:
                    f.write(raw_search or "")
            except:
                pass

            if not raw_search:
                print("❌ No products found. Try a different search.\n")
                continue

            products = parse_json_safely(raw_search)
            if not products:
                print("❌ Could not parse products. Try again.\n")
                continue

            products_text = format_products_for_analyzer(products)

            # Analyze (suppress stdout)
            analyzer_prompt = create_analyzer_prompt(user_input, products_text)
            sys_sav = sys.stdout
            sys.stdout = StringIO()
            chat_analyzer = product_analyzer.initiate_chat(
                tool_executor, message=analyzer_prompt, max_turns=1
            )
            sys.stdout = sys_sav

            # Extract analyzer reply (avoid prompt echo)
            recommendations = ""
            for msg in reversed(chat_analyzer.chat_history):
                if msg.get("name") == "ProductAnalyzerAgent":
                    content = (msg.get("content") or "").strip()
                    if content and "PRODUCT #1" in content and "PRODUCT #3" in content:
                        recommendations = content
                        break

            if not recommendations:
                print("❌ Could not analyze products.\n")
                continue

            print("="*70)
            print("✨ TOP 3 RECOMMENDATIONS FOR YOU")
            print("="*70 + "\n")
            print(recommendations)
            print("\n" + "="*70 + "\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)[:120]}")
            print("Please try another query.\n")


if __name__ == "__main__":
    main()