import re
import uuid
from pathlib import Path


def slugify(text: str, max_length: int = 50) -> str:
    slug = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    slug = re.sub(r"[\s_-]+", "-", slug.strip()).strip("-").lower()
    return slug[:max_length] or "video"


def make_run_dir(base: Path, prefix: str = "") -> Path:
    run_id = f"{prefix}{uuid.uuid4().hex[:8]}" if prefix else uuid.uuid4().hex[:8]
    run_dir = base / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir
