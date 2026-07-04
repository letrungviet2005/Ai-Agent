from app.models.product import Product
from app.agents.script_agent import ScriptAgent

product = Product(
    name="Quạt mini cầm tay",
    price="199000",
    description="""
Pin 4000mAh
100 cấp gió
Nhỏ gọn
Dùng 8 tiếng
""",
    target_customer="Sinh viên và nhân viên văn phòng"
)

agent = ScriptAgent()

result = agent.generate(product)

print(result)