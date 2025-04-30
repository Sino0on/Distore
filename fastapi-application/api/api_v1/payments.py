from typing import Annotated

from fastapi import APIRouter, Depends, Request, BackgroundTasks, Body
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.fastapi_users import current_active_user
from core.config import settings
from core.models import db_helper, User
from core.models.order import OrderStatus
from core.schemas.payments import PaymentSignature, PaymentResult
from services.delivery import DeliveryService
from services.orders import OrderService
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
    order_service = OrderService(session)
    data = await request.form()
    result = await service.result_url_handler(data, background_tasks)
    try:
        payment_data = PaymentResult(**data)
        order = await order_service._get_order(payment_data.pg_order_id)
        if order.status == OrderStatus.paid:
            sdek_service = DeliveryService(session, settings.redis.url, settings.sdek_config.client_id, settings.sdek_config.client_secret)
            await sdek_service.create_order(order)
    except Exception as e:
        logger.error(e)

    return result


@router.post("/get_payment_url")
async def get_payment_url(
        user: Annotated[User, Depends(current_active_user)],
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        order_id: int = Body(..., embed=True),
):
    service = PaymentsService(session)

    return await service.get_payment_url(user, order_id)