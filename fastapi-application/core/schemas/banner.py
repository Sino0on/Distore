from __future__ import annotations

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
