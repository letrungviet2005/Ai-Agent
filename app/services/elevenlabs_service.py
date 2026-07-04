from pathlib import Path

import httpx

from app.core.config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID


class ElevenLabsService:
    def __init__(self, voice_id: str | None = None, api_key: str | None = None):
        self.voice_id = voice_id or ELEVENLABS_VOICE_ID
        self.api_key = api_key or ELEVENLABS_API_KEY
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY chưa được cấu hình trong .env")

    def synthesize(self, text: str, output_path: Path) -> Path:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            output_path.write_bytes(response.content)

        return output_path
