from app.agents.base_agent import BaseAgent
from app.models.product import Product
from app.models.script import Script
from app.prompts.script_prompt import SCRIPT_SYSTEM, build_script_prompt


class ScriptAgent(BaseAgent):
    def generate(self, product: Product) -> Script:
        prompt = build_script_prompt(product)
        data = self.llm.generate_json(prompt, system=SCRIPT_SYSTEM)
        return Script.model_validate(data)
