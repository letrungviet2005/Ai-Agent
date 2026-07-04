from pydantic import BaseModel


class VideoResult(BaseModel):
    file_path: str
    duration: float
    width: int
    height: int
