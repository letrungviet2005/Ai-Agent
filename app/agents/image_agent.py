from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.core.config import OUTPUT_DIR
from app.models.image import ImageResult, SceneImage
from app.models.product import Product
from app.models.script import Script
from app.prompts.image_prompt import build_scene_image_prompt
from app.services.image_generation_service import ImageGenerationService
from app.utils.file import make_run_dir
from app.utils.image import create_scene_storyboard_image


class ImageAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.image_service = ImageGenerationService()

    def generate(
        self,
        product: Product,
        script: Script,
        output_dir: Path | None = None,
    ) -> ImageResult:
        run_dir = output_dir or make_run_dir(OUTPUT_DIR / "images")
        run_dir.mkdir(parents=True, exist_ok=True)
        scene_images: list[SceneImage] = []

        for scene in script.scenes:
            prompt = build_scene_image_prompt(product, scene)
            file_path = run_dir / f"scene_{scene.id:02d}.png"
            generated = self.image_service.generate(prompt, file_path)

            if not generated:
                create_scene_storyboard_image(
                    product_name=product.name,
                    price=product.price,
                    scene_visual=scene.visual,
                    text_overlay=scene.text_overlay,
                    dest=file_path,
                )

            scene_images.append(
                SceneImage(
                    scene_id=scene.id,
                    file_path=str(file_path),
                    prompt=prompt,
                    provider=self.image_service.provider,
                    fallback=not generated,
                )
            )

        return ImageResult(scenes=scene_images, output_dir=str(run_dir))
