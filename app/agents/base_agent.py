from app.core.llm import LLMService


class BaseAgent:
    def __init__(self):
        self.llm = LLMService()
