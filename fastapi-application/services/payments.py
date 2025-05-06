import hashlib

import aiohttp
import xmltodict
from core.config import settings
from core.models import User, Order
from core.models.order import OrderStatus
from core.schemas.payments import (
    PaymentSignature,
    PaymentResult,
    PaymentRequestParams,
    PaymentUrlResponse,
)
from fastapi import HTTPException, Response, BackgroundTasks, status
from loguru import logger
from services.driver_1c import Driver1C
from services.orders import OrderService
from services.uds import UDSService
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import FormData


class PaymentsService:
    REQUIRED_PARAMS = {
        "pg_order_id",
        "pg_merchant_id",
        "pg_amount",
        "pg_description",
        "pg_salt",
    }
    PAYMENT_RESULT_MAIN_PARAMS = {
        "pg_payment_id",
        "pg_result",
        "pg_can_reject",
    }

    def __init__(self, session):
        self.session: AsyncSession = session
        self.order_service = OrderService(session)
        self.driver_1c = Driver1C()

    async def _generate_signature(
            self,
            params: dict,
            script_name: str = "init_payment.php"):
        # Сортировка параметров и генерация подписи
        sorted_params = dict(sorted(params.items()))
        signature_elements = [script_name] + [
            str(value)
            for value in sorted_params.values()
        ]
        signature_elements.append(settings.freedom_pay_config.secret_key)
        signature_string = ";".join(signature_elements)
        signature = hashlib.md5(signature_string.encode("utf-8")).hexdigest()

        return PaymentSignature(signature=signature, params=params)

    async def generate_signature(
            self, user: User,
            params: dict,
            script_name: str = "init_payment.php",
    ):
        await self.validate_payments_params(user, params)

        return await self._generate_signature(params, script_name)

    async def validate_payments_params(self, user: User, params: dict):
        # Проверка на обязательные параметры
        missing_params = self.REQUIRED_PARAMS - params.keys()

        if missing_params:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required parameters: {', '.join(missing_params)}",
            )

        payment_result_params = self.PAYMENT_RESULT_MAIN_PARAMS.intersection(
            params.keys()
        )

        if payment_result_params:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid parameters for init payment: {', '.join(payment_result_params)}",
            )

        # Проверка, что все параметры начинаются с "pg_"
        for key in params.keys():
            if not key.startswith("pg_"):
                raise HTTPException(
                    status_code=400,
                    detail=f"All parameters must start with 'pg_'. Invalid parameter: '{key}'",
                )

        merchant_id = int(params["pg_merchant_id"])

        if not merchant_id == settings.freedom_pay_config.merchant_id:
            raise HTTPException(status_code=400, detail="Invalid merchant id")

        order_id = int(params["pg_order_id"])
        order = await self.order_service.get_order(user, order_id)

    async def check_signature(self, signature: str, params: dict,
                              script_name: str):
        generated_sig = await self._generate_signature(params, script_name)

        if generated_sig.signature != signature:
            logger.error(f"Invalid signature: {signature} | params: {params}")
            return False

        return True

    async def result_url_handler(
            self, data: FormData, background_tasks: BackgroundTasks
    ):
        logger.debug(f"Requesting payment result url")
        logger.debug(f"Request data: {data}")

        invalid_data = False
        check_signature = False

        try:
            payment_data = PaymentResult(**data)
            logger.info(
                f"Requesting payment result for order: {payment_data.pg_order_id} "
                f"| payment_id: {payment_data.pg_payment_id}"
            )
        except Exception as e:
            logger.error(e)
            invalid_data = True

        if not invalid_data:
            check_signature = await self.check_signature(
                data.get('pg_sig', ''),
                data,
                "result_url",
            )

        if invalid_data:
            pg_status = "error"
            pg_description = "Некорректные данные"
            order_status = OrderStatus.error
        elif not check_signature:
            pg_status = "error"
            pg_description = "Подпись (pg_sig) не прошла проверку"
            order_status = OrderStatus.error

        # Логика проверки pg_result
        elif payment_data.pg_result == 1:  # Успех
            pg_status = "ok"
            pg_description = "Заказ оплачен"
            order_status = OrderStatus.paid
        elif (
                payment_data.pg_can_reject == 1 and payment_data.pg_result == 0
        ):  # Отказ при условии, что pg_can_reject == 1
            pg_status = "rejected"
            pg_description = "Платеж отменен"
            order_status = OrderStatus.canceled
        else:
            pg_status = "error"
            pg_description = "Ошибка в интерпретации данных"
            order_status = OrderStatus.error

        order = None
        is_new_order = False
        if not invalid_data:
            try:
                order, is_new_order = await self.order_service.payment_update(
                    order_id=int(payment_data.pg_order_id),
                    status=order_status,
                    payment_data={**data},
                )
            except HTTPException as e:
                logger.error(e)
                pg_status = "error"
                pg_description = "Ошибка обновления заказа: Заказ не найден"
                order = None
            except Exception as e:
                logger.error(e)
                pg_status = "error"
                pg_description = "Ошибка обновления заказа"
                order = None

        # Генерация ответа
        response_signature = await self._generate_signature(
            {
                "pg_status": pg_status,
                "pg_description": pg_description,
                "pg_salt": data.get("pg_salt", ""),
            },
            "result_url",
        )

        response_xml = f"""<?xml version="1.0" encoding="utf-8"?>
        <response>
            <pg_status>{pg_status}</pg_status>
            <pg_description>{pg_description}</pg_description>
            <pg_salt>{data.get("pg_salt", "")}</pg_salt>
            <pg_sig>{response_signature.signature}</pg_sig>
        </response>"""

        if order and pg_status == "ok" and is_new_order:
            background_tasks.add_task(
                self.send_create_1c_order_request,
                order,
            )

            if order.uds_transaction_id is None:
                uds_service = UDSService(self.session, order.user)
                try:
                    uds_transaction = await uds_service.create_transaction(
                        phone_number=order.user.phone_number,
                        total_price=order.total_price,
                        points=0,
                    )
                except Exception as e:
                    logger.error(
                        f"Error creating uds transaction for order: {order.id}"
                        )
                    logger.error(e)

        return Response(content=response_xml, media_type="application/xml")

    async def send_create_1c_order_request(self, order: Order) -> None:
        data = await self.driver_1c.create_1c_order(order)

        if not data:
            raise Exception("Error creating order in 1C: Empty response")

        order_1c_number = data.get("OrderNumber")

        if not order_1c_number:
            raise Exception(
                "Error creating order in 1C: Order number not found"
                )

        await self.order_service.update_order_code_1c(
            order.id, order_1c_number
            )

    async def get_payment_url(
            self,
            user: User,
            order_id: int,
    ) -> PaymentUrlResponse:
        order = await self.order_service.get_order(user, order_id)

        params = {
            "pg_order_id": order.id,
            "pg_merchant_id": settings.freedom_pay_config.merchant_id,
            "pg_amount": order.final_price,
            "pg_currency": "KGS",
            "pg_description": f"Order #{order.id}\nCustomer: {user.nickname}",
            "pg_salt": 'distore',
        }

        signature = await self._generate_signature(params)

        request_params = PaymentRequestParams(
            pg_sig=signature.signature,
            **params,
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=settings.freedom_pay_config.init_payment_url,
                    params={
                        "pg_sig": signature.signature,
                        **request_params.dict(),
                    },
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Error getting payment URL",
                    )

                response_text = await response.text()
                response_data = xmltodict.parse(response_text)["response"]

                logger.info(f"Response text: {response_text}")
                logger.info(f"Response data: {response_data}")

            if response_data.get("pg_status") != "ok":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error getting payment URL",
                )

        await self.check_signature(
            response_data.pop("pg_sig"),
            response_data,
            "init_payment.php",
        )

        return PaymentUrlResponse(
            redirect_url=response_data["pg_redirect_url"]
        )


