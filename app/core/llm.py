from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )

        self.model = os.getenv("LLM_MODEL")

    def generate(self, prompt: str):
        response = self.client.chat.completions.create(
    model=self.model,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

        return response.choices[0].message.content