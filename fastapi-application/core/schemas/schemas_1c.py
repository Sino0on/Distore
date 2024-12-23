from typing import List, Optional
from pydantic import BaseModel, EmailStr, constr


class Property1C(BaseModel):
    name: str
    value: str


class Variation1C(BaseModel):
    properties: List[Property1C]


class Product1C(BaseModel):
    code_1c: str
    variation_code_1c: str
    variation: Variation1C
    quantity: int


class Customer1C(BaseModel):
    name: str
    phone: str
    email: EmailStr
    country: str
    city: str
    address: str
    note: Optional[str] = None


class Order1C(BaseModel):
    order_id: int
    products: List[Product1C]
    customer: Customer1C