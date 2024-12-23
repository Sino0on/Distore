from typing import Annotated, List

from fastapi import APIRouter, Depends, Body, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.fastapi_users import current_active_user
from core.config import settings
from core.models import db_helper, User
from core.schemas.order import (
    OrderRead,
    OrderCreate,
    OrderUDSDiscountSchema,
    OrderProductReadWithOrderId,
)
from services.orders import OrderService

router = APIRouter(
    prefix=settings.api.v1.orders,
    tags=["Orders"],
)


@router.get("", response_model=List[OrderRead])
async def get_orders(
    user: Annotated[
        User,
        Depends(current_active_user),
    ]
):

    return user.orders


@router.get("/order_products", response_model=List[OrderProductReadWithOrderId])
async def get_order_products_by_user(
    user: Annotated[
        User,
        Depends(current_active_user),
    ],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    service = OrderService(session)

    return await service.get_order_products_by_user(user)


@router.post("/create_from_cart", response_model=OrderRead)
async def create_order_from_cart(
    user: Annotated[
        User,
        Depends(current_active_user),
    ],
    order_data: OrderCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    service = OrderService(session)

    return await service.create_order_from_cart(user, order_data=order_data)


@router.post("/set_uds_discount/", response_model=OrderRead)
async def set_order_uds_discount(
    user: Annotated[
        User,
        Depends(current_active_user),
    ],
    discount_data: OrderUDSDiscountSchema,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    service = OrderService(session)

    return await service.set_order_uds_discount(user, discount_data)


@router.post("/set_delivery/", response_model=OrderRead)
async def set_order_delivery(
    user: Annotated[
        User,
        Depends(current_active_user),
    ],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    order_id: int = Body(...),
    delivery: bool = Body(...),
):
    service = OrderService(session)

    return await service.set_order_delivery(user, order_id, delivery)


@router.delete("/delete/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    user: Annotated[
        User,
        Depends(current_active_user),
    ],
    order_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    service = OrderService(session)

    return await service.delete_order(user, order_id)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    user: Annotated[
        User,
        Depends(current_active_user),
    ],
    order_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    service = OrderService(session)

    return await service.get_order(user, order_id)
