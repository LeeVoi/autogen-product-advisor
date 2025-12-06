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
            "model": "gemini-2.5-flash",
            "api_key": GEMINI_API_KEY,
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "stream": False,
            # just to silence the pricing warning
            "price": [0.0, 0.0],
        }
    ]
}
