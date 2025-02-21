import requests
import os

class APIRouter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"  # Official Open Router endpoint

    def generate(self, prompt, model="openai/gpt-3.5-turbo"):  # Default model
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "prompt": prompt, "max_tokens": 100}
        try:
            response = requests.post(f"{self.base_url}/completions", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["choices"][0]["text"].strip()
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None