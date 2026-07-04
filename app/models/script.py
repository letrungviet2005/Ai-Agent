from pydantic import BaseModel, Field


class Scene(BaseModel):
    id: int
    duration: float
    voiceover: str
    visual: str
    text_overlay: str


class Script(BaseModel):
    title: str
    duration_seconds: int
    hook: str
    scenes: list[Scene]
    cta: str
    hashtags: list[str] = Field(default_factory=list)
