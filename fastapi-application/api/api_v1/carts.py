from typing import Annotated

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.fastapi_users import current_active_user
from core.config import settings
from core.models import db_helper, User
from core.schemas.cart import CartRead, CartAddProductSchema, CartRemoveProductSchema
from services.carts import CartService

router = APIRouter(
    prefix=settings.api.v1.carts,
    tags=["Carts"],
)


@router.get("", response_model=CartRead)
async def get_cart(
        user: Annotated[
            User,
            Depends(current_active_user),
        ]
) -> CartRead:

    return user.cart


@router.post("/add_product", response_model=CartRead)
async def add_product_to_cart(
        user: Annotated[
            User,
            Depends(current_active_user),
        ],
        data: CartAddProductSchema,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> CartRead:
    cart_service = CartService(session)
    return await cart_service.add_product_to_cart(user, data)


@router.post("/remove_product")
async def remove_product_from_cart(
        user: Annotated[
            User,
            Depends(current_active_user),
        ],
        product_remove_data: CartRemoveProductSchema,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> CartRead:
    cart_service = CartService(session)
    return await cart_service.remove_product_from_cart(user, product_remove_data)


@router.post("/update_quantity")
async def update_product_in_cart(
        user: Annotated[
            User,
            Depends(current_active_user),
        ],
        data: CartAddProductSchema,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> CartRead:
    cart_service = CartService(session)
    return await cart_service.update_product_quantity(user, data)


@router.post("/clear")
async def clear_cart(
        user: Annotated[
            User,
            Depends(current_active_user),
        ],
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> CartRead:
    cart_service = CartService(session)
    return await cart_service.clear_cart(user)
