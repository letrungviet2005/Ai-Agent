from io import BytesIO
from pathlib import Path

import httpx
import numpy as np
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

from app.core.config import VIDEO_HEIGHT, VIDEO_WIDTH

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def download_images(urls: list[str], dest_dir: Path) -> list[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    with httpx.Client(timeout=20.0, headers=DEFAULT_HEADERS, follow_redirects=True) as client:
        for index, url in enumerate(urls[:5]):
            try:
                response = client.get(url)
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").lower()
                if content_type and not content_type.startswith("image/"):
                    continue

                with Image.open(BytesIO(response.content)) as image:
                    image.load()
                    normalized = image.convert("RGB")

                path = dest_dir / f"image_{index + 1}.jpg"
                normalized.save(path, format="JPEG", quality=92, optimize=True)
                saved.append(path)
            except (httpx.HTTPError, OSError, UnidentifiedImageError):
                continue

    return saved


def create_placeholder_image(title: str, price: str, dest: Path) -> Path:
    image = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color=(20, 20, 30))
    draw = ImageDraw.Draw(image)
    font_title = get_font(64)
    font_price = get_font(48)

    draw.text((60, 800), title[:40], fill="white", font=font_title)
    draw.text((60, 920), price, fill=(255, 200, 50), font=font_price)
    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest)
    return dest


def _fit_cover(image: Image.Image, width: int, height: int) -> Image.Image:
    ratio = max(width / image.width, height / image.height)
    resized = image.resize(
        (int(image.width * ratio), int(image.height * ratio)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def _wrap_text(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        bbox = font.getbbox(test)
        if bbox[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines or [text[:60]]


def render_scene_frame(
    image_path: Path,
    text_overlay: str,
    price: str,
    product_name: str,
) -> np.ndarray:
    with Image.open(image_path) as image:
        base = image.convert("RGB")
    frame = _fit_cover(base, VIDEO_WIDTH, VIDEO_HEIGHT)
    draw = ImageDraw.Draw(frame)

    overlay = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(
        (0, VIDEO_HEIGHT - 420, VIDEO_WIDTH, VIDEO_HEIGHT),
        fill=(0, 0, 0, 170),
    )
    frame = Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(frame)

    font_overlay = get_font(52)
    font_meta = get_font(36)
    lines = _wrap_text(text_overlay, font_overlay, VIDEO_WIDTH - 120)

    y = VIDEO_HEIGHT - 360
    for line in lines[:3]:
        draw.text((60, y), line, fill="white", font=font_overlay)
        y += 62

    draw.text((60, VIDEO_HEIGHT - 120), price, fill=(255, 210, 60), font=font_meta)
    draw.text((60, 60), product_name[:35], fill="white", font=font_meta)

    return np.array(frame)
