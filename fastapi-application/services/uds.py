from datetime import datetime

import requests
from fastapi import HTTPException
from loguru import logger
from requests.auth import HTTPBasicAuth
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.schemas.uds import UDSDataRead, UDSTransactionData
from core.config import settings


class UDSService:
    UDS_CUSTOMER_FIND_URL = settings.uds_config.uds_customer_find_url
    UDS_TRANSACTION_CALC_URL = settings.uds_config.uds_transaction_calc_url
    UDS_TRANSACTION_CREATE_URL = settings.uds_config.uds_transaction_create_url
    UDS_TRANSACTION_REFUND_URL = settings.uds_config.uds_transaction_refund_url

    AUTH = HTTPBasicAuth(settings.uds_config.username, settings.uds_config.password)

    def __init__(self, session, user):
        self.session: AsyncSession = session
        self.user: User = user

    @staticmethod
    def _default_headers():
        return {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "Content-Type": "application/json",
            "X-Origin-Request-Id": settings.uds_config.origin_request_id,
            "X-Timestamp": datetime.utcnow().isoformat(),
        }

    async def get_uds_points(self, uds_code: str) -> UDSDataRead:
        logger.info(f"Requesting UDS points for code: {uds_code} | user: {self.user}")

        response = requests.get(
            url=self.UDS_CUSTOMER_FIND_URL,
            params={"code": uds_code},
            auth=self.AUTH,
            headers=self._default_headers(),
        )

        logger.info(f"Response (UDS customer find) status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            return UDSDataRead(
                uid=data["user"]["uid"],
                points=data["user"]["participant"]["points"],
            )

        if response.status_code == 404:
            data = response.json()
            raise HTTPException(
                status_code=400,
                detail=f'Error code: {data["errorCode"]}\nMessage: {data["message"]}',
            )

        raise HTTPException(
            status_code=400,
            detail=f"UDS reqeust error\n"
            f"URL: {response.url}\n"
            f"Status code: {response.status_code}",
        )

    async def create_transaction(
        self,
        total_price: int | float,
        points: int,
        uds_code: str = None,
        phone_number: str = None,
    ) -> UDSTransactionData:
        if not uds_code and points > 0:
            raise HTTPException(
                status_code=400,
                detail="To withdraw points you need to provide uds code",
            )

        if not uds_code and not phone_number:
            raise HTTPException(
                status_code=400,
                detail="To create uds transaction you need to provide uds code or phone number",
            )

        logger.info(
            f"Requesting UDS create transaction for code: {uds_code} | user: {self.user}"
        )

        if uds_code:
            calc_data = await self.calculate_transaction_info(
                uds_code, total_price, points
            )

        if uds_code:
            payload = {
                "code": uds_code,
                "receipt": {
                    "total": total_price,
                    "cash": calc_data["cash"],
                    "points": points,
                },
            }
        else:
            payload = {
                "participant": {"phone": phone_number},
                "receipt": {
                    "total": total_price,
                    "cash": total_price,
                    "points": points,
                },
            }

        response = requests.post(
            url=self.UDS_TRANSACTION_CREATE_URL,
            json=payload,
            auth=self.AUTH,
            headers=self._default_headers(),
        )

        logger.info(
            f"Response (UDS create transaction) status code: {response.status_code}"
        )

        if response.status_code == 200:
            return UDSTransactionData(**response.json())

        if response.status_code == 404:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid uds code: {uds_code}",
            )

        if response.status_code == 400:
            data = response.json()
            raise HTTPException(
                status_code=400,
                detail=f'Error code: {data["errorCode"]}\nMessage: {data["message"]}',
            )

        raise HTTPException(
            status_code=400,
            detail=f"UDS reqeust error\n"
            f"URL: {response.url}\n"
            f"Status code: {response.status_code}",
        )

    async def refund_transaction(self, transaction_id: int) -> None:
        logger.info(f"Requesting UDS refund for transaction: {transaction_id}")

        response = requests.post(
            url=self.UDS_TRANSACTION_REFUND_URL,
            json={"id": transaction_id},
            auth=self.AUTH,
            headers=self._default_headers(),
        )

        logger.info(f"Response (UDS refund) status code: {response.status_code}")

    async def calculate_transaction_info(
        self,
        uds_code: str,
        total_price: int,
        points: int,
    ) -> dict:
        logger.info(
            f"Requesting UDS transaction calculation for code: {uds_code} | user: {self.user}"
        )

        response = requests.post(
            url=self.UDS_TRANSACTION_CALC_URL,
            json={
                "code": uds_code,
                "receipt": {"total": total_price, "points": points},
            },
            auth=self.AUTH,
            headers=self._default_headers(),
        )

        logger.info(
            f"Response (UDS transaction calculation) status code: {response.status_code}"
        )

        if response.status_code == 200:
            data = response.json()
            return data["purchase"]

        if response.status_code == 404:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid uds code: {uds_code}",
            )

        raise HTTPException(
            status_code=400,
            detail=f"UDS reqeust error\n"
            f"URL: {response.url}\n"
            f"Status code: {response.status_code}",
        )
