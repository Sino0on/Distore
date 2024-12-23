from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import Category, db_helper
from core.schemas.category import GroupRead, CategoryRead
from services.categories import CategoryService

router = APIRouter(
    prefix=settings.api.v1.categories,
    tags=["Categories"],
)


@router.get("", response_model=list[GroupRead])
async def get_categories(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[GroupRead]:
    service = CategoryService(session)
    groups = await service.get_categories()

    return groups


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Category:
    service = CategoryService(session)
    return await service.get_category(category_id)
