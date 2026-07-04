import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
        )
        self.model = os.getenv("LLM_MODEL")

    def _build_messages(self, prompt: str, system: str | None = None) -> list[dict]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return messages

    def generate(self, prompt: str, system: str | None = None) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self._build_messages(prompt, system),
        )
        return response.choices[0].message.content

    def generate_json(self, prompt: str, system: str | None = None) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self._build_messages(prompt, system),
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)
