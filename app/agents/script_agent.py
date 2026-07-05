from app.agents.base_agent import BaseAgent
from app.models.product import Product
from app.models.script import Script
from app.prompts.script_prompt import SCRIPT_SYSTEM, build_script_prompt


class ScriptAgent(BaseAgent):
    def generate(self, product: Product) -> Script:
        prompt = build_script_prompt(product)
        data = self.llm.generate_json(prompt, system=SCRIPT_SYSTEM)
        script = Script.model_validate(data)
        return self._focus_script(script)

    def _focus_script(self, script: Script) -> Script:
        scenes = script.scenes[:4]
        for index, scene in enumerate(scenes, start=1):
            scene.id = index
            scene.duration = min(max(scene.duration, 4), 6)
            scene.voiceover = self._limit_words(scene.voiceover, 18)
            scene.text_overlay = self._limit_words(scene.text_overlay, 8)

        script.scenes = scenes
        script.duration_seconds = round(sum(scene.duration for scene in scenes))
        return script

    def _limit_words(self, text: str, max_words: int) -> str:
        words = text.split()
        if len(words) <= max_words:
            return text
        return " ".join(words[:max_words]).rstrip(" ,.;:-")
