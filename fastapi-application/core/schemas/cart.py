from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class CartProductImageRead(BaseModel):
    id: int
    url: str


class ProductForCartRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    images: List[CartProductImageRead] = []


class ProductPropertyForCartRead(BaseModel):
    id: int
    name: str
    value: str


class ProductVariationForCartRead(BaseModel):
    id: int
    price: float
    quantity: int
    properties: List[ProductPropertyForCartRead]
    product: ProductForCartRead


class CartProductRead(BaseModel):
    id: int
    quantity: int
    product_variation: ProductVariationForCartRead


class CartRead(BaseModel):
    id: int
    total_price: float
    products: list[CartProductRead]


class CartAddProductSchema(BaseModel):
    variation_id: int
    quantity: int = Field(default=1, ge=1)


class CartRemoveProductSchema(BaseModel):
    product_variation_id: int
