from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, Query
import httpx
from fastapi.responses import JSONResponse

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
    service = DeliveryService(session, settings.redis.url, settings.sdek_config.client_id, settings.sdek_config.client_secret)
    return await service.get_status(order_id)






@router.get("/cdek/cities")
async def fetch_cities(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    name: str = Query(...),
    country_code: str = Query("RU"),
):
    service = DeliveryService(session, settings.redis.url, settings.sdek_config.client_id, settings.sdek_config.client_secret)
    cities = await service.get_cities(name=name, country_code=country_code)
    return cities

