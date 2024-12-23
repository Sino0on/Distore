from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper
from core.schemas.brand import BrandRead
from services.brands import BrandService

router = APIRouter(
    prefix=settings.api.v1.brands,
    tags=["Brands"],
)


@router.get("/", response_model=list[BrandRead])
async def get_brands(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    service = BrandService(session)

    return await service.get_all_brands()


@router.get("/random_list", response_model=list[BrandRead])
async def get_random_brands_list(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    count: int = Query(20, ge=1, le=100),
):
    service = BrandService(session)

    return await service.get_random_brands_list(count)
