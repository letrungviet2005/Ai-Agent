from app.models.product import Product
from app.models.script import Scene


def build_scene_image_prompt(product: Product, scene: Scene) -> str:
    return f"""Use case: ads-marketing
Asset type: vertical 9:16 TikTok product video scene image
Primary request: Create one polished visual image for this scene.
Product: {product.name}
Price: {product.price}
Product description: {product.description}
Scene visual: {scene.visual}
Scene overlay context: {scene.text_overlay}
Style/medium: realistic commercial product/lifestyle photography, clean e-commerce ad quality
Composition/framing: vertical portrait, centered subject, clear focus, enough negative space for captions
Lighting/mood: bright, attractive, modern Vietnamese social-commerce style
Constraints: no embedded text, no watermark, no logo hallucination, no UI buttons, no distorted product, no extra unrelated objects
Avoid: blurry image, dark empty background, unreadable text, collage layout, screenshot style"""
