import requests
import os
import time
from utils.logger import logger  # Ensure logger import

class APIRouter:
    def __init__(self):
        self.api_key = os.getenv("OPEN_ROUTER_KEY")
        self.base_url = "https://openrouter.ai/api/v1"

    def generate(self, prompt, model="gemini/2.0-flash"):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 100}
        try:
            resp = requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"API error: {e}")
            time.sleep(60)
            return None