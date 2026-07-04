from dataclasses import dataclass
from pathlib import Path

from app.agents.product_agent import ProductAgent
from app.agents.script_agent import ScriptAgent
from app.agents.video_agent import VideoAgent
from app.agents.voice_agent import VoiceAgent
from app.core.config import OUTPUT_DIR
from app.models.product import Product
from app.models.script import Script
from app.models.video import VideoResult
from app.models.voice import VoiceResult
from app.utils.file import make_run_dir


@dataclass
class PipelineResult:
    product: Product
    script: Script
    voice: VoiceResult
    video: VideoResult
    run_dir: Path


class CreateVideoWorkflow:
    def __init__(self):
        self.product_agent = ProductAgent()
        self.script_agent = ScriptAgent()
        self.voice_agent = VoiceAgent()
        self.video_agent = VideoAgent()

    def run_from_url(self, url: str) -> PipelineResult:
        product = self.product_agent.fetch_from_url(url)
        return self.run_from_product(product)

    def run_from_product(self, product: Product) -> PipelineResult:
        run_dir = make_run_dir(OUTPUT_DIR / "runs")
        scripts_dir = run_dir / "scripts"
        audio_dir = run_dir / "audio"
        videos_dir = run_dir / "videos"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script = self.script_agent.generate(product)
        self._save_json(scripts_dir / "product.json", product)
        self._save_json(scripts_dir / "script.json", script)

        voice = self.voice_agent.generate(script, output_dir=audio_dir)
        video = self.video_agent.generate(product, script, voice, output_dir=videos_dir)

        return PipelineResult(
            product=product,
            script=script,
            voice=voice,
            video=video,
            run_dir=run_dir,
        )

    def _save_json(self, path: Path, model) -> None:
        path.write_text(model.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")
