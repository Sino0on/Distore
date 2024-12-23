from typing import Annotated

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.fastapi_users import current_active_user
from core.config import settings
from core.models import db_helper, User
from core.schemas.uds import UDSDataRead
from services.uds import UDSService

router = APIRouter(
    prefix=settings.api.v1.uds,
    tags=["UDS"],
)


@router.get("/points", response_model=UDSDataRead)
async def get_uds_points(
    user: Annotated[
        User,
        Depends(current_active_user),
    ],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    uds_code: Annotated[str, Query(...)],
):
    service = UDSService(session, user)

    return await service.get_uds_points(uds_code)
