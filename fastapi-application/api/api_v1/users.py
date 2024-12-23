from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.fastapi_users import fastapi_users
from core.config import settings
from core.models import User, db_helper
from api.api_v1.fastapi_users import current_active_user
from core.schemas.user import (
    UserRead,
    UserUpdate, AddressRead, AddressCreate, AddressUpdate,
)
from services.addresses import AddressService

router = APIRouter(
    prefix=settings.api.v1.users,
    tags=["Users"],
)

# /me
# /{id}
router.include_router(
    router=fastapi_users.get_users_router(
        UserRead,
        UserUpdate,
    ),
)


@router.post("/address/create", response_model=AddressRead)
async def create_address(
    user: Annotated[
        User,
        Depends(current_active_user),
    ],
    address_data: AddressCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    service = AddressService(session, user)

    return await service.create_address(address_data)


@router.patch("/address/update", response_model=AddressRead)
async def update_address(
    user: Annotated[
        User,
        Depends(current_active_user),
    ],
    address_data: AddressUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    service = AddressService(session, user)

    return await service.update_address(address_data)


@router.get("/address/get", response_model=AddressRead)
async def get_address(
    user: Annotated[
        User,
        Depends(current_active_user),
    ],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    service = AddressService(session, user)

    return await service.get_address_by_user()