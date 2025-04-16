from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import Category, db_helper
from core.schemas.category import GroupRead, CategoryRead
from services.categories import CategoryService
from services.delivery import DeliveryService

router = APIRouter(
    prefix=settings.api.v1.delivery,
    tags=["Delivery"],
)


@router.get("/{order_id}", response_model=None)
async def get_order(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    order_id: str,
) -> list[GroupRead]:
    service = DeliveryService(session, settings.sdek_config.client_id, settings.sdek_config.client_secret)
    return await service.get_status(order_id)

