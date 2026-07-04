from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str
    price: str
    description: str
    target_customer: str = "Người tiêu dùng Việt Nam"
    url: str | None = None
    platform: str | None = None
    images: list[str] = Field(default_factory=list)
    category: str | None = None
    rating: float | None = None
    sold_count: int | None = None
