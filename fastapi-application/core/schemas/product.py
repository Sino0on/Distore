from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from core.schemas.base import BaseWithORM, PaginationMetadata

from core.schemas.brand import BrandRead


class CategoryForProductRead(BaseWithORM):
    id: int
    name: str


class ProductPropertyRead(BaseWithORM):
    id: int
    name: str
    value: str


class ProductVariationRead(BaseWithORM):
    id: int
    price: float
    quantity: int
    properties: List[ProductPropertyRead]


class ProductImageRead(BaseWithORM):
    id: int
    url: str


class ProductRead(BaseWithORM):
    id: int
    title: str
    description: Optional[str] = None
    brand: BrandRead | None = None
    category: CategoryForProductRead
    images: List[ProductImageRead] = []
    variations: List[ProductVariationRead]


    class Config:
        from_attributes = True


# Входные схемы для создания/обновления
class ProductPropertyCreateSchema(BaseWithORM):
    uuid_1c: Optional[str]
    name: str
    value: str


class ProductVariationCreateSchema(BaseWithORM):
    uuid_1c: str
    name: str
    price: float = Field(..., gt=0)
    quantity: int
    sale_quantity: Optional[int] = 0

    properties: List[ProductPropertyCreateSchema]


class ProductImageCreateSchema(BaseWithORM):
    url: str


class ProductCreateSchema(BaseWithORM):
    uuid_1c: str
    title: str
    description: Optional[str] = None
    brand_id: int | None = None
    category_id: int
    images: List[ProductImageCreateSchema] | None = []
    variations: List[ProductVariationCreateSchema] | None = []


class ProductPropertiesFilter(BaseWithORM):
    properties: Optional[List[str]] = []


class ProductResponseWithPagination(BaseWithORM):
    items: list[ProductRead]
    pagination: PaginationMetadata
    properties: List[ProductPropertyRead] = []