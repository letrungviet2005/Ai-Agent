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
    image = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color=(18, 24, 38))
    draw = ImageDraw.Draw(image)
    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        red = int(18 + ratio * 18)
        green = int(24 + ratio * 50)
        blue = int(38 + ratio * 42)
        draw.line((0, y, VIDEO_WIDTH, y), fill=(red, green, blue))

    font_title = get_font(58)
    font_price = get_font(46)
    font_label = get_font(30)

    draw.rounded_rectangle((70, 280, VIDEO_WIDTH - 70, 1120), radius=36, fill=(255, 255, 255))
    draw.rounded_rectangle((120, 350, VIDEO_WIDTH - 120, 720), radius=28, fill=(235, 241, 247))
    draw.text((150, 460), "ẢNH SẢN PHẨM", fill=(60, 70, 85), font=font_label)
    draw.text((150, 510), "chưa tải được", fill=(60, 70, 85), font=font_label)

    title_lines = _wrap_text(title, font_title, VIDEO_WIDTH - 220)
    y = 770
    for line in title_lines[:3]:
        draw.text((120, y), line, fill=(20, 28, 42), font=font_title)
        y += 68
    draw.text((120, 1010), price, fill=(220, 120, 20), font=font_price)
    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest)
    return dest


def create_scene_storyboard_image(
    product_name: str,
    price: str,
    scene_visual: str,
    text_overlay: str,
    dest: Path,
) -> Path:
    image = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color=(246, 248, 250))
    draw = ImageDraw.Draw(image)

    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        red = int(238 - ratio * 16)
        green = int(244 - ratio * 28)
        blue = int(248 - ratio * 30)
        draw.line((0, y, VIDEO_WIDTH, y), fill=(red, green, blue))

    font_label = get_font(30)
    font_title = get_font(54)
    font_body = get_font(38)
    font_overlay = get_font(64)
    font_price = get_font(42)

    draw.rounded_rectangle((70, 80, VIDEO_WIDTH - 70, 280), radius=28, fill=(22, 32, 48))
    _draw_wrapped_text(
        draw=draw,
        text=product_name,
        xy=(110, 116),
        font=font_title,
        fill="white",
        max_width=VIDEO_WIDTH - 220,
        line_height=62,
        max_lines=2,
    )

    draw.rounded_rectangle((70, 340, VIDEO_WIDTH - 70, 1260), radius=36, fill=(255, 255, 255))
    draw.text((110, 390), "Hình ảnh cần tạo từ scene.visual", fill=(90, 100, 115), font=font_label)
    _draw_wrapped_text(
        draw=draw,
        text=scene_visual,
        xy=(110, 460),
        font=font_body,
        fill=(28, 38, 52),
        max_width=VIDEO_WIDTH - 220,
        line_height=52,
        max_lines=12,
    )

    draw.rounded_rectangle(
        (110, 1320, VIDEO_WIDTH - 110, 1570),
        radius=30,
        fill=(255, 240, 214),
    )
    _draw_wrapped_text(
        draw=draw,
        text=text_overlay,
        xy=(150, 1365),
        font=font_overlay,
        fill=(18, 24, 36),
        max_width=VIDEO_WIDTH - 300,
        line_height=74,
        max_lines=2,
    )

    draw.text((110, VIDEO_HEIGHT - 180), price, fill=(210, 100, 24), font=font_price)
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


def _draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int] | str,
    max_width: int,
    line_height: int,
    max_lines: int,
) -> int:
    x, y = xy
    lines = _wrap_text(text, font, max_width)
    for line in lines[:max_lines]:
        draw.text((x, y), line, fill=fill, font=font)
        y += line_height
    return y


def render_scene_frame(
    image_path: Path,
    text_overlay: str,
    price: str,
    product_name: str,
    visual_text: str = "",
    show_visual_card: bool = False,
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
    font_visual = get_font(38)
    font_visual_title = get_font(44)

    if show_visual_card and visual_text:
        card_left = 70
        card_top = 360
        card_right = VIDEO_WIDTH - 70
        card_bottom = 1180
        draw.rounded_rectangle(
            (card_left, card_top, card_right, card_bottom),
            radius=32,
            fill=(255, 255, 255),
        )
        draw.text(
            (card_left + 42, card_top + 42),
            "Nội dung cảnh",
            fill=(24, 34, 48),
            font=font_visual_title,
        )
        _draw_wrapped_text(
            draw=draw,
            text=visual_text,
            xy=(card_left + 42, card_top + 120),
            font=font_visual,
            fill=(45, 55, 70),
            max_width=card_right - card_left - 84,
            line_height=50,
            max_lines=11,
        )

    lines = _wrap_text(text_overlay, font_overlay, VIDEO_WIDTH - 120)

    y = VIDEO_HEIGHT - 360
    for line in lines[:3]:
        draw.text((60, y), line, fill="white", font=font_overlay)
        y += 62

    draw.text((60, VIDEO_HEIGHT - 120), price, fill=(255, 210, 60), font=font_meta)
    draw.text((60, 60), product_name[:35], fill="white", font=font_meta)

    return np.array(frame)
