import asyncio
import re
import time
from pathlib import Path

import edge_tts
import numpy as np
from moviepy.editor import AudioClip

from app.core.config import TTS_VOICE

FALLBACK_VOICES = ("vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural")


class EdgeTTSService:
    def __init__(self, voice: str | None = None):
        self.voice = voice or TTS_VOICE

    def synthesize(self, text: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        clean_text = self._clean_text(text)
        voices = self._voice_candidates()
        last_error: Exception | None = None

        for voice in voices:
            for attempt in range(2):
                try:
                    if output_path.exists():
                        output_path.unlink()
                    asyncio.run(self._synthesize_async(clean_text, output_path, voice))
                    if output_path.exists() and output_path.stat().st_size > 0:
                        return output_path
                except Exception as exc:
                    last_error = exc
                    time.sleep(0.4 * (attempt + 1))

        duration = self._estimate_duration(clean_text)
        self._write_silence(output_path, duration)
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError(f"Edge TTS failed and silent fallback was not created: {last_error}")
        return output_path

    async def _synthesize_async(self, text: str, output_path: Path, voice: str) -> None:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))

    def _voice_candidates(self) -> list[str]:
        voices = [self.voice, *FALLBACK_VOICES]
        result: list[str] = []
        for voice in voices:
            if voice and voice not in result:
                result.append(voice)
        return result

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"[\x00-\x1f\x7f]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text or " "

    def _estimate_duration(self, text: str) -> float:
        words = max(1, len(text.split()))
        return max(2.0, min(8.0, words / 2.6 + 0.5))

    def _write_silence(self, output_path: Path, duration: float) -> None:
        clip = AudioClip(lambda t: np.zeros_like(t), duration=duration, fps=44100)
        try:
            clip.write_audiofile(
                str(output_path),
                fps=44100,
                nbytes=2,
                codec="libmp3lame",
                logger=None,
            )
        finally:
            clip.close()
