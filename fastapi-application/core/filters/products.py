from typing import Optional

from fastapi import Query
from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from core.filters.brand import BrandFilter
from core.filters.category import CategoryFilter
from core.models import Product
from core.models.product import ProductProperty, ProductVariation
from pydantic import BaseModel
from typing import List


# Модель для одного свойства
class PropertyFilter(BaseModel):
    name: str
    value: str

# Модель для тела запроса
class ProductFilterRequest(BaseModel):
    properties: List[PropertyFilter]


class ProductVariationFilter(Filter, extra="allow"):
    price__gte: Optional[float] = Field(None, ge=0, alias="priceMin")
    price__lte: Optional[float] = Field(None, ge=0, alias="priceMax")

    class Constants(Filter.Constants):
        model = ProductVariation


class ProductFilter(Filter, extra="allow"):
    brand: Optional[BrandFilter] = FilterDepends(with_prefix("brand", BrandFilter))
    category: Optional[CategoryFilter] = FilterDepends(with_prefix("category", CategoryFilter))
    price__gte: Optional[float] = Field(Query(None, ge=0, alias="priceMin"))
    price__lte: Optional[float] = Field(Query(None, ge=0, alias="priceMax"))

    search: Optional[str] = None

    class Constants(Filter.Constants):
        model = Product
        search_model_fields = ["title"]
