from app.models.product import Product

SCRIPT_SYSTEM = """Bạn là chuyên gia viết kịch bản TikTok bán hàng tại Việt Nam.
Luôn trả về JSON hợp lệ theo đúng schema được yêu cầu.
Ngôn ngữ: tiếng Việt tự nhiên, gần gũi, đi thẳng vào lợi ích chính của sản phẩm."""


def build_script_prompt(product: Product) -> str:
    images_hint = ""
    if product.images:
        images_hint = f"\nẢnh sản phẩm có sẵn: {len(product.images)} ảnh."

    return f"""Viết 1 kịch bản TikTok bán hàng ngắn, tập trung vào ý chính cho sản phẩm sau.

Tên: {product.name}
Giá: {product.price}
Mô tả: {product.description}
Khách hàng mục tiêu: {product.target_customer}
Danh mục: {product.category or "Không rõ"}{images_hint}

Yêu cầu bắt buộc:
- Tổng thời lượng mục tiêu: 18-24 giây, tuyệt đối không viết lan man.
- Chỉ 3-4 scene, mỗi scene tập trung vào 1 ý: vấn đề, lợi ích chính, bằng chứng/ưu đãi, CTA.
- Hook mạnh trong 2 giây đầu.
- Voiceover mỗi scene tối đa 18 từ, câu ngắn, dễ đọc bằng TTS.
- Text overlay mỗi scene tối đa 8 từ.
- Không nhắc quá nhiều thông số phụ; chỉ chọn 1-2 điểm bán hàng nổi bật nhất.
- CTA rõ ràng cuối video.
- 4-6 hashtag phù hợp TikTok Shop Việt Nam.

Trả về JSON với schema:
{{
  "title": "string",
  "duration_seconds": 22,
  "hook": "string",
  "scenes": [
    {{
      "id": 1,
      "duration": 5,
      "voiceover": "lời thoại ngắn, đi thẳng vào ý chính",
      "visual": "mô tả hình ảnh/cảnh quay",
      "text_overlay": "text ngắn trên màn hình"
    }}
  ],
  "cta": "string",
  "hashtags": ["#tag1", "#tag2"]
}}"""
