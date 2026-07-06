from pydantic import BaseModel, Field


class SceneImage(BaseModel):
    scene_id: int
    file_path: str
    prompt: str
    provider: str
    fallback: bool = False


class ImageResult(BaseModel):
    scenes: list[SceneImage] = Field(default_factory=list)
    output_dir: str = ""
