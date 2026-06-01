from __future__ import annotations

import httpx

from app.llm.base import BaseLLM


class OllamaProvider(BaseLLM):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self._base_url = base_url.rstrip("/")
        self._model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = httpx.post(
            f"{self._base_url}/api/chat",
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
