from app.core.llm import LLMService

class ScriptAgent:

    def __init__(self):
        self.llm = LLMService()

    def generate(self, product):

        prompt = f"""
Bạn là chuyên gia TikTok.

Viết 3 kịch bản TikTok.

Tên:
{product.name}

Giá:
{product.price}

Mô tả:
{product.description}

Khách hàng:
{product.target_customer}

Yêu cầu:
- Hook mạnh 3 giây đầu
- Dài khoảng 40 giây
- Có CTA cuối.
"""

        return self.llm.generate(prompt)