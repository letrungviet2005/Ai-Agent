import base64
from pathlib import Path

import httpx
from openai import OpenAI

from app.core.config import IMAGE_API_KEY, IMAGE_BASE_URL, IMAGE_MODEL, IMAGE_PROVIDER, IMAGE_SIZE


class ImageGenerationService:
    def __init__(self):
        self.provider = IMAGE_PROVIDER.lower()
        self.model = IMAGE_MODEL
        self.size = IMAGE_SIZE
        self.client = None

        if self.provider == "openai" and IMAGE_API_KEY:
            self.client = OpenAI(api_key=IMAGE_API_KEY, base_url=IMAGE_BASE_URL)

    def generate(self, prompt: str, output_path: Path) -> bool:
        if not self.client:
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=self.size,
                n=1,
            )
            image = response.data[0]

            if getattr(image, "b64_json", None):
                output_path.write_bytes(base64.b64decode(image.b64_json))
                return True

            if getattr(image, "url", None):
                with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                    downloaded = client.get(image.url)
                    downloaded.raise_for_status()
                    output_path.write_bytes(downloaded.content)
                return True
        except Exception:
            return False

        return False
