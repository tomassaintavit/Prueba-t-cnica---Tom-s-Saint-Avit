from __future__ import annotations

from openai import OpenAI

from app.llm.base import BaseLLM


class GroqProvider(BaseLLM):
    def __init__(self, api_key: str, model: str = "llama3-70b-8192"):
        self._client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        self._model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )
        return response.choices[0].message.content or ""
