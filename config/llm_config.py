import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Use Google gemini API key."
        "Add it to your environment or to a .env file."
    )

LLM_CONFIG = {
    "config_list": [
        {
            "model": "gemini-2.5-flash-lite",
            "api_type": "google",
            "api_key": GEMINI_API_KEY,
            "api_rate_limit": 0.1,  # 10 requests per second
            "max_retries": 1,
            "num_predict": 1,
            "repeat_penalty": 1.0,
            "stream": False,
            "native_tool_calls": False,
            "seed": 23,
            "cache_seed": None,
            "timeout": 30,
            # just to silence the pricing warning
            "price": [0.0, 0.0],
        }
    ]
}
