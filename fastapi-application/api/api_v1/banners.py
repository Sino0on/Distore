from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import Category, db_helper
from core.schemas.banner import BannerRead
from core.schemas.category import GroupRead, CategoryRead
from services.banners import BannerService
from services.categories import CategoryService

router = APIRouter(
    prefix=settings.api.v1.banners,
    tags=["Banners"],
)


@router.get("", response_model=list[BannerRead])
async def get_banners(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    accept_language: str = Header("ru")
) -> list[GroupRead]:
    service = BannerService(session)
    groups = await service.get_banners()
    return groups
    # return [GroupRead.from_orm_with_locale(group, accept_language) for group in groups]


@router.get("/{banner_id}", response_model=BannerRead)
async def get_banner(
    category_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Category:
    service = BannerService(session)
    return await service.get_banner(category_id)
