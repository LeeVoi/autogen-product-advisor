# Autogen Product Advisor

An interactive, multi-agent shopping assistant built on AutoGen that searches products from DummyJSON, analyzes candidates against user constraints (price, rating, availability), and provides concise recommendations with an internal critic review.

Highlights:
- Uses Google Gemini via `google-generativeai` (optional Vertex AI support).
- Separates responsibilities across agents: Search Orchestrator, Product Analyzer, Internal Critic, Tool Executor.
- Robust product fetching with safe field handling and compact presentation to the analyzer.

Overview
- You type a shopping request (e.g., “smartphone around $300, rating at least 4”).
- The Search Orchestrator extracts a keyword and calls product tools to fetch candidates.
- The Product Analyzer selects 2–3 recommendations and explains the reasoning.
- The Internal Critic reviews recommendations for clarity and constraint alignment.

Architecture
- `agents/ProductSearchOrchestrator`: LLM agent that decides which product tools to call and must return a final ```json fenced block.
- `agents/tool_executor_agent`: Executes tool calls (no analysis) and returns results to the orchestrator.
- `agents/product_analyzer_agent`: Ranks and explains recommendations based on user constraints.
- `agents/product_internal_critic_agent`: Approves or flags the analyzer’s output.
- `tools/product_api.py`: Product data access (DummyJSON) and light normalization.
- `utils/output_formatter.py`: JSON block extraction and formatting for analyzer prompts.

Prerequisites
- Python 3.12.0 (recommended), wont work with higher python.
- A Google Gemini API key in `.env` file.

To avoid package conflicts, create a new venv and do the following:

Setup (Windows PowerShell)
Run these commands in the project root `E:\Projects\School\autogen-product-advisor`:

```powershell
# Create and activate a virtual environment
python -m venv .venv (or name it anything you want).
.\.venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip (uptional)

# Install dependencies
python -m pip install -r requirements.txt

# Set up environment variables (edit .env)
# Ensure the file contains your Gemini key
# Example:
#   GEMINI_API_KEY=YOUR_KEY_HERE
```

If you prefer Vertex AI clients, `requirements.txt` already includes `vertexai` and `google-cloud-aiplatform`. Using Vertex requires additional GCP setup (project, auth, location) which is beyond the scope of this quick start.
But these packages were added because it will throw an exception at runtime otherwise.

Exception caused by:
`api_type: google`,

Configuration
- `.env`:
	- `GEMINI_API_KEY`: required for Google Gemini.
- `config/llm_config.py` controls model and API type. Defaults to `gemini-2.5-flash-lite` via Google.

Run
```powershell
python main.py
```

You’ll see a banner and a prompt. Example inputs:
- `find me a laptop`
- `phones under $300`
- `smartphone around 200, rating at least 4`

Type `exit`, `quit`, or `q` to leave.

How It Works
1. Search step: The Search Orchestrator suggests tool calls like `search_products(query="laptop", limit=20)`.
2. Tool Executor runs those calls and returns the raw data.
3. Orchestrator returns a final ```json fenced object with `products`, `total`, and `query`.
4. Analyzer formats a compact list and selects 2–3 recommendations with reasoning.
5. Internal Critic approves or provides a short rejection message.

Troubleshooting
- No products parsed / empty results:
	- The orchestrator must end with a ```json fenced block. If the first keyword is poor (e.g., typo), the orchestrator can retry with another query. We allow multiple tool calls before finalizing.
- KeyError on `availabilityStatus`:
	- We safely derive availability from `stock` when the API doesn’t provide `availabilityStatus`.
- Dependency warnings (e.g., FLAML AutoML not installed):
	- These are benign; we don’t use AutoML functionality.
- Rate limit or cost warnings:
	- `llm_config.py` sets a dummy price array to silence pricing logs. Adjust model or settings as needed.

Repo Structure
- `main.py`: CLI entrypoint and the three-step flow (Search → Analyze → Critic).
- `agents/`: Agent definitions and prompts.
- `tools/`: Product API client utilities.
- `utils/`: Formatting helpers for passing compact product lists to the analyzer.
- `config/llm_config.py`: LLM configuration and environment loading.
- `requirements.txt`: Python dependencies.
- `docs/`: Design docs and use cases.

Notes
- This project uses AutoGen fork `autogen-agentchat` plus `autogen==0.3.1`.
- Ensure network access to `https://dummyjson.com/products`.
- For Vertex/GCP usage, configure credentials if needed (`gcloud auth application-default login`) and project settings per Google Cloud docs (mostly not needed when using google-generativeai with a regular Gemini API key.).

License
This repository is for educational use. No specific license declared.