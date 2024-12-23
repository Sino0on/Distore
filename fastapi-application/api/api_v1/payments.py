from typing import Annotated

from fastapi import APIRouter, Depends, Request, BackgroundTasks
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.fastapi_users import current_active_user
from core.config import settings
from core.models import db_helper, User
from core.schemas.payments import PaymentSignature, PaymentResult
from services.payments import PaymentsService

router = APIRouter(
    prefix=settings.api.v1.payments,
    tags=["Payments"],
)


@router.get(
    "/generate_signature",
    response_model=PaymentSignature,
)
async def generate_signature(
    request: Request,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    """
        Generate signature for FreedomPay payment

         - **Обязательные параметры**:
            - `pg_order_id` (int): ID заказа
            - `pg_merchant_id` (int): ID мерчанта
            - `pg_amount` (int): Сумма платежа
            - `pg_description` (str): Описание заказа
            - `pg_salt` (str): Соль для генерации подписи
        - **Необязательные параметры**:
            - Любые другие параметры, начинающиеся с префикса `pg_`, будут включены в генерацию подписи.
        - **Query параметры**:
            - Параметры должны быть переданы в query-строке запроса.

        **Пример запроса**:
        ```
        /generate_signature?pg_order_id=123&pg_merchant_id=456&pg_amount=100&pg_description=test&pg_salt=random_salt
        ```
        """

    service = PaymentsService(session)

    return await service.generate_signature(user, dict(request.query_params))


@router.post("/result_url")
async def result_url(
        request: Request,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        background_tasks: BackgroundTasks,
):
    service = PaymentsService(session)

    data = await request.form()
    return await service.result_url_handler(data, background_tasks)

