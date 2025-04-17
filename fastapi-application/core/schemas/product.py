from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from core.schemas.base import BaseWithORM, PaginationMetadata

from core.schemas.brand import BrandRead


class CategoryForProductRead(BaseWithORM):
    id: int
    name: str
    name_ky: str
    name_en: str


class ProductPropertyRead(BaseWithORM):
    id: int = None
    name: str
    value: str


class ProductImageRead(BaseWithORM):
    id: int
    url: str
    is_main: bool


class ProductVariationImageRead(ProductImageRead):
    pass


class ProductVariationRead(BaseWithORM):
    id: int
    price: float
    quantity: int
    properties: List[ProductPropertyRead]
    images: List[ProductVariationImageRead] = []


class ProductRead(BaseWithORM):
    id: int
    title: str
    title_ky: Optional[str] = None
    title_en: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    description_ky: Optional[str] = None
    usingmethod: Optional[str] = None
    composition: Optional[str] = None
    brand: BrandRead | None = None
    category: CategoryForProductRead
    images: List[ProductImageRead] = []
    variations: List[ProductVariationRead]
    main_image: ProductImageRead | None = None


    class Config:
        from_attributes = True


# Входные схемы для создания/обновления
class ProductPropertyCreateSchema(BaseWithORM):
    uuid_1c: Optional[str]
    name: str
    value: str


class ProductImageCreateSchema(BaseWithORM):
    url: str
    is_main: bool


class ProductVariationImageCreateSchema(ProductImageCreateSchema):
    pass


class ProductVariationCreateSchema(BaseWithORM):
    uuid_1c: str
    name: str
    price: float = Field(..., gt=0)
    quantity: int
    sale_quantity: Optional[int] = 0

    properties: List[ProductPropertyCreateSchema]
    images: List[ProductVariationImageCreateSchema] = []


class ProductCreateSchema(BaseWithORM):
    uuid_1c: str
    title: str
    description: Optional[str] = None
    usingmethod: Optional[str] = None
    composition: Optional[str] = None
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