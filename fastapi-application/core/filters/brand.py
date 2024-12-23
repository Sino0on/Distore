from typing import Optional

from fastapi.params import Query
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from core.models import Brand


class BrandFilter(Filter, extra="allow"):
    name__in: Optional[list[str]] = Field(
        Query(
            None,
            alias="brandName",
            description="Example: `'ello'` or `'tom ford,alfaparf'`",
        )
    )

    class Constants(Filter.Constants):
        model = Brand
