import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "edge")
TTS_VOICE = os.getenv("TTS_VOICE", "vi-VN-HoaiMyNeural")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "google")
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY") or os.getenv("LLM_API_KEY")
IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL")
IMAGE_MODEL = os.getenv("IMAGE_MODEL")
IMAGE_SIZE = os.getenv("IMAGE_SIZE", "1024x1536")

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
