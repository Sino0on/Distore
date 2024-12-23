from fastapi import Query
from pydantic import BaseModel

from core.config import settings


class Pagination(BaseModel):
    page: int = Query(1, ge=1)
    page_size: int = Query(settings.page_size_default, ge=1, le=1000)
