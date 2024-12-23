from typing import Optional

from fastapi.params import Query
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from core.models import Category


class CategoryFilter(Filter, extra="allow"):
    name__in: Optional[list[str]] = Field(
        Query(
            None,
            alias="categoryName",
            description="Example: `'Маски'` or `'Шампуни," "Мужской парфюм'`",
        )
    )

    class Constants(Filter.Constants):
        model = Category
