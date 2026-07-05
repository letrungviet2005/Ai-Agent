from pathlib import Path

from PIL import Image
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

from app.agents.base_agent import BaseAgent
from app.core.config import OUTPUT_DIR, VIDEO_FPS, VIDEO_HEIGHT, VIDEO_WIDTH
from app.models.product import Product
from app.models.script import Script
from app.models.video import VideoResult
from app.models.voice import VoiceResult
from app.utils.file import make_run_dir, slugify
from app.utils.image import (
    create_placeholder_image,
    download_images,
    render_scene_frame,
)


class VideoAgent(BaseAgent):
    def generate(
        self,
        product: Product,
        script: Script,
        voice: VoiceResult,
        output_dir: Path | None = None,
    ) -> VideoResult:
        run_dir = output_dir or make_run_dir(OUTPUT_DIR / "videos")
        assets_dir = run_dir / "assets"
        frames_dir = run_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        image_paths = download_images(product.images, assets_dir)
        placeholder = assets_dir / "placeholder.jpg"
        if not image_paths:
            create_placeholder_image(product.name, product.price, placeholder)
            image_paths = [placeholder]

        clips = []
        scene_map = {item.scene_id: item for item in voice.scenes}

        for index, scene in enumerate(script.scenes):
            audio_scene = scene_map.get(scene.id)
            if not audio_scene:
                continue

            image_path = image_paths[index % len(image_paths)]
            frame_path = frames_dir / f"scene_{scene.id:02d}.jpg"
            show_visual_card = image_path == placeholder
            try:
                frame_array = render_scene_frame(
                    image_path=image_path,
                    text_overlay=scene.text_overlay,
                    price=product.price,
                    product_name=product.name,
                    visual_text=scene.visual,
                    show_visual_card=show_visual_card,
                )
            except OSError:
                if not placeholder.exists():
                    create_placeholder_image(product.name, product.price, placeholder)
                frame_array = render_scene_frame(
                    image_path=placeholder,
                    text_overlay=scene.text_overlay,
                    price=product.price,
                    product_name=product.name,
                    visual_text=scene.visual,
                    show_visual_card=True,
                )
            Image.fromarray(frame_array).save(frame_path)

            audio_clip = AudioFileClip(audio_scene.file_path)
            duration = max(audio_clip.duration + 0.2, scene.duration)

            video_clip = (
                ImageClip(frame_array)
                .set_duration(duration)
                .set_audio(audio_clip)
                .set_fps(VIDEO_FPS)
            )
            clips.append(video_clip)

        if not clips:
            raise ValueError("Không có scene nào để tạo video")

        final = concatenate_videoclips(clips, method="compose")
        output_path = run_dir / f"{slugify(script.title)}.mp4"

        total_duration = final.duration

        final.write_videofile(
            str(output_path),
            fps=VIDEO_FPS,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4,
            logger=None,
        )

        for clip in clips:
            clip.close()
        final.close()

        return VideoResult(
            file_path=str(output_path),
            duration=total_duration,
            width=VIDEO_WIDTH,
            height=VIDEO_HEIGHT,
        )
