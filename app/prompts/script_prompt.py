from app.models.product import Product

SCRIPT_SYSTEM = """Bạn là chuyên gia viết kịch bản TikTok bán hàng tại Việt Nam.
Luôn trả về JSON hợp lệ theo đúng schema được yêu cầu.
Ngôn ngữ: tiếng Việt tự nhiên, gần gũi, phù hợp Gen Z và Millennials."""


def build_script_prompt(product: Product) -> str:
    images_hint = ""
    if product.images:
        images_hint = f"\nẢnh sản phẩm có sẵn: {len(product.images)} ảnh."

    return f"""Viết 1 kịch bản TikTok bán hàng cho sản phẩm sau.

Tên: {product.name}
Giá: {product.price}
Mô tả: {product.description}
Khách hàng mục tiêu: {product.target_customer}
Danh mục: {product.category or "Không rõ"}{images_hint}

Yêu cầu:
- Hook mạnh trong 3 giây đầu
- Tổng thời lượng khoảng 40 giây
- Chia thành 4-6 scene, mỗi scene có voiceover, mô tả hình ảnh, text overlay
- CTA rõ ràng cuối video
- 5-8 hashtag phù hợp TikTok Shop Việt Nam

Trả về JSON với schema:
{{
  "title": "string",
  "duration_seconds": 40,
  "hook": "string",
  "scenes": [
    {{
      "id": 1,
      "duration": 5,
      "voiceover": "lời thoại",
      "visual": "mô tả hình ảnh/cảnh quay",
      "text_overlay": "text hiển thị trên màn hình"
    }}
  ],
  "cta": "string",
  "hashtags": ["#tag1", "#tag2"]
}}"""
