from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from core.schemas.product import ProductRead


class BannerRead(BaseModel):
    id: int
    title: str
    title_ky: str
    title_en: str
    description: str
    description_ru: str
    description_ky: str
    status: bool
    products: list[ProductRead]


# Схемы для валидации данных
class BannerCreateSchema(BaseModel):
    image: str
    title: str
    title_ky: Optional[str] = None
    title_en: Optional[str] = None
    description: str
    description_ky: Optional[str] = None
    description_en: Optional[str] = None
    product_ids: Optional[List[int]] = Field(default_factory=list)
    status: bool = True

class BannerUpdateSchema(BaseModel):
    image: Optional[str] = None
    title: Optional[str] = None
    title_ky: Optional[str] = None
    title_en: Optional[str] = None
    description: Optional[str] = None
    description_ky: Optional[str] = None
    description_en: Optional[str] = None
    product_ids: Optional[List[int]] = None
    status: Optional[bool] = None

class BannerResponseSchema(BaseModel):
    id: int
    image: str
    title: str
    title_ky: Optional[str] = None
    title_en: Optional[str] = None
    description: str
    description_ky: Optional[str] = None
    description_en: Optional[str] = None
    created_at: datetime
    product_ids: Optional[str] = None
    status: bool

    class Config:
        from_attributes = True
