import asyncio
from pathlib import Path

import edge_tts

from app.core.config import TTS_VOICE


class EdgeTTSService:
    def __init__(self, voice: str | None = None):
        self.voice = voice or TTS_VOICE

    def synthesize(self, text: str, output_path: Path) -> Path:
        asyncio.run(self._synthesize_async(text, output_path))
        return output_path

    async def _synthesize_async(self, text: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(str(output_path))
