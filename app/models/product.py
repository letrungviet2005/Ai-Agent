from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: str
    description: str
    target_customer: str