from __future__ import annotations

import os

from app.llm.base import BaseLLM
from app.llm.ollama_provider import OllamaProvider
from app.llm.openai_provider import OpenAIProvider


def get_llm() -> BaseLLM:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        return OpenAIProvider(api_key=api_key)

    if provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        return OllamaProvider(base_url=base_url, model=model)

    raise ValueError(f"Unknown LLM provider: {provider}")
