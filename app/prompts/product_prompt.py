PRODUCT_EXTRACT_SYSTEM = """Bạn trích xuất thông tin sản phẩm từ nội dung trang web e-commerce Việt Nam.
Luôn trả về JSON hợp lệ theo schema được yêu cầu."""


def build_product_extract_prompt(url: str, page_text: str) -> str:
    truncated = page_text[:8000]
    return f"""Trích xuất thông tin sản phẩm từ URL và nội dung trang sau.

URL: {url}

Nội dung trang:
{truncated}

Trả về JSON:
{{
  "name": "tên sản phẩm",
  "price": "giá (giữ nguyên định dạng, ví dụ 199.000đ hoặc 199000)",
  "description": "mô tả ngắn gọn các điểm nổi bật",
  "target_customer": "đối tượng khách hàng phù hợp",
  "category": "danh mục sản phẩm hoặc null",
  "images": ["url ảnh nếu tìm thấy"],
  "rating": null,
  "sold_count": null
}}"""


def build_target_customer_prompt(name: str, description: str, category: str | None) -> str:
    return f"""Dựa trên sản phẩm sau, xác định 1 đối tượng khách hàng mục tiêu ngắn gọn (1 câu).

Tên: {name}
Danh mục: {category or "Không rõ"}
Mô tả: {description}

Trả về JSON: {{"target_customer": "..."}}"""
