from fastapi import APIRouter, Depends, HTTPException, Header, status
from typing import Annotated
from core.schemas.banner import BannerCreateSchema, BannerUpdateSchema, BannerRead
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
    banner_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Category:
    service = BannerService(session)
    return await service.get_banner(banner_id)


@router.post("", response_model=BannerRead, status_code=status.HTTP_201_CREATED)
async def create_banner(
    banner_data: BannerCreateSchema,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> BannerRead:
    service = BannerService(session)
    banner = await service.create_banner(banner_data)
    if not banner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create banner")
    return banner

@router.put("/{banner_id}", response_model=BannerRead)
async def update_banner(
    banner_id: int,
    banner_data: BannerUpdateSchema,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> BannerRead:
    service = BannerService(session)
    banner = await service.update_banner(banner_id, banner_data)
    if not banner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
    return banner

@router.delete("/{banner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_banner(
    banner_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    service = BannerService(session)
    success = await service.delete_banner(banner_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
    return None