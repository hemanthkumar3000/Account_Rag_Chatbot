import os
import requests

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def call_llm(prompt: str, temperature: float = 0.2) -> str:
    """
    Call Ollama locally to generate a reply for the given prompt.
    """
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": temperature,
    }

    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()

    result = resp.json()
    return result.get("response", "")