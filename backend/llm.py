from pydantic import BaseModel
from typing import Optional
import os

import google.generativeai as genai  # type: ignore


class LLMResponse(BaseModel):
    reply: str
    tokens_used: int


def configure_gemini():
    """
    Configure the Gemini client using LLM_API_KEY from the environment.
    """
    api_key = os.getenv("LLM_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("LLM_API_KEY (or GOOGLE_API_KEY / GEMINI_API_KEY) is not set in environment")
    genai.configure(api_key=api_key)


def call_llm(prompt: str, temperature: float = 0.2) -> LLMResponse:
    configure_gemini()

    try:
        model = genai.GenerativeModel("gemini-1.0-pro")

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
            ),
        )

        reply_text = response.text.strip() if hasattr(response, "text") else ""
        tokens_used = len(prompt) + len(reply_text)

        return LLMResponse(reply=reply_text, tokens_used=tokens_used)

    except Exception as e:
        err_msg = str(e)
        print(f"[DEBUG] LLM (Gemini) error: {err_msg}")  # <- important
        return LLMResponse(
            reply="There was a problem contacting the Gemini language model service.",
            tokens_used=0,
        )