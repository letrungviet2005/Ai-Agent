from pathlib import Path

from moviepy.editor import AudioFileClip

from app.agents.base_agent import BaseAgent
from app.core.config import OUTPUT_DIR, TTS_PROVIDER
from app.models.script import Script
from app.models.voice import AudioScene, VoiceResult
from app.services.edge_tts_service import EdgeTTSService
from app.services.elevenlabs_service import ElevenLabsService
from app.utils.file import make_run_dir


class VoiceAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.tts = self._create_tts_service()

    def _create_tts_service(self):
        if TTS_PROVIDER == "elevenlabs":
            return ElevenLabsService()
        return EdgeTTSService()

    def generate(self, script: Script, output_dir: Path | None = None) -> VoiceResult:
        run_dir = output_dir or make_run_dir(OUTPUT_DIR / "audio")
        audio_scenes: list[AudioScene] = []

        for scene in script.scenes:
            file_path = run_dir / f"scene_{scene.id:02d}.mp3"
            self.tts.synthesize(scene.voiceover, file_path)

            with AudioFileClip(str(file_path)) as audio:
                duration = audio.duration

            audio_scenes.append(
                AudioScene(
                    scene_id=scene.id,
                    file_path=str(file_path),
                    duration=duration,
                    text=scene.voiceover,
                )
            )

        return VoiceResult(
            scenes=audio_scenes,
            output_dir=str(run_dir),
        )
