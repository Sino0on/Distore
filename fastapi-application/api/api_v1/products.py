from fastapi import APIRouter, Depends, Body
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.fastapi_users import current_active_user
from api.dependencies.pagination import Pagination
from api.dependencies.product.ordering import Ordering
from core.config import settings
from core.filters.products import ProductFilter, ProductFilterRequest
from core.models import db_helper, User
from core.schemas.product import ProductRead, ProductResponseWithPagination
from services.products import ProductService

router = APIRouter(
    prefix=settings.api.v1.products,
    tags=["Products"],
)


@router.post("", response_model=ProductResponseWithPagination)
async def get_products(
    product_filter_request: ProductFilterRequest,
    product_filter: ProductFilter = FilterDepends(ProductFilter),
    order_by: Ordering = Depends(Ordering),
    pagination: Pagination = Depends(Pagination),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> list[ProductRead]:
    properties = product_filter_request.properties
    service = ProductService(session)
    products = await service.get_products(
        product_filter, pagination, order_by, properties
    )

    return products


@router.get("/new", response_model=ProductResponseWithPagination)
async def get_new_products(
    session: AsyncSession = Depends(db_helper.session_getter),
    pagination: Pagination = Depends(Pagination),
) -> list[ProductRead]:
    service = ProductService(session)

    return await service.get_new_products(pagination)


@router.get("/bestselling", response_model=ProductResponseWithPagination)
async def get_bestselling_products(
    session: AsyncSession = Depends(db_helper.session_getter),
    pagination: Pagination = Depends(Pagination),
) -> list[ProductRead]:
    service = ProductService(session)

    return await service.get_bestselling_products(pagination)


@router.get("/favorites/list", response_model=ProductResponseWithPagination)
async def get_favorite_products(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
    pagination: Pagination = Depends(Pagination),
) -> list[ProductRead]:
    service = ProductService(session)

    return await service.get_favorite_products(user, pagination)


@router.post("/favorites/set")
async def set_favorite_product(
    product_id: int = Body(..., embed=True),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    service = ProductService(session)

    return await service.set_favorite_product(user, product_id)


@router.post("/favorites/unset")
async def unset_favorite_product(
    product_id: int = Body(..., embed=True),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    service = ProductService(session)

    return await service.unset_favorite_product(user, product_id)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> ProductRead:
    service = ProductService(session)

    return await service.get_product(product_id)
