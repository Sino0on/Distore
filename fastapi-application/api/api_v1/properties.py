from tracemalloc import Filter

from fastapi import APIRouter, Depends, Query, Body
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.fastapi_users import current_active_user
from api.dependencies.pagination import Pagination
from api.dependencies.product.ordering import Ordering
from core.config import settings
from core.filters.products import ProductFilter, ProductFilterRequest
from core.models import db_helper, User
from core.schemas.product import ProductRead, ProductPropertyRead
from services.products import ProductService

router = APIRouter(
    prefix=settings.api.v1.products,
    tags=["properties"],
)


@router.get("/properties", response_model=list[ProductPropertyRead])
async def get_properties(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> list[ProductPropertyRead]:
    service = ProductService(session)
    properties = await service.get_properties()

    return properties
