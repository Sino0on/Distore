from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, model_validator

from core.schemas.product import ProductImageRead, ProductVariationRead


class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: str
    country: str
    country_code: str
    city: str
    city_uuid: str
    city_code: str
    address: str
    comment: str | None = None
    promo_code: str | None = None
    use_saved_address: bool = False

    @model_validator(mode="before")
    @classmethod
    def skip_fields_if_saved_address(cls, values):
        # Если use_saved_address=True, пропускаем валидацию остальных полей
        if values.get("use_saved_address"):
            for field in cls.model_fields.keys():
                if field == "use_saved_address":
                    continue
                values[field] = "string"
        return values


class ProductForOrderRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    images: List[ProductImageRead] = []


class ProductVariationForOrderRead(ProductVariationRead):
    product: ProductForOrderRead


class OrderProductRead(BaseModel):
    product_variation: ProductVariationForOrderRead
    quantity: int


class OrderRead(BaseModel):
    id: int
    sdek_id: str | None = None
    customer_name: str
    customer_phone: str
    customer_email: str
    country: str
    city: str
    address: str
    comment: str | None = None
    promo_code: str | None = None
    status: str
    total_price: int | float
    delivery: bool
    discount: int
    final_price: int | float
    created_at: datetime
    updated_at: datetime
    products: list[OrderProductRead]


class OrderUDSDiscountSchema(BaseModel):
    order_id: int
    uds_code: str
    points: int


class OrderProductReadWithOrderId(OrderProductRead):
    id: int
    order_id: int