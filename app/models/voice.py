from pydantic import BaseModel, Field


class AudioScene(BaseModel):
    scene_id: int
    file_path: str
    duration: float
    text: str


class VoiceResult(BaseModel):
    scenes: list[AudioScene] = Field(default_factory=list)
    combined_path: str | None = None
    output_dir: str = ""
