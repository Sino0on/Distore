from pprint import pprint
from typing import List
from unittest.mock import patch

import aiohttp
from loguru import logger
from sqlalchemy import select, desc, asc, Select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload, aliased, contains_eager, load_only

from api.dependencies.pagination import Pagination
from api.dependencies.product.ordering import Ordering
from core.filters.products import ProductFilter, PropertyFilter
from core.models import Product, Category, CategoryProperty, Brand, User, Order
from core.schemas import PaginationMetadata
from core.models.product import ProductVariation, ProductProperty
from core.schemas.product import ProductPropertiesFilter, ProductResponseWithPagination
import redis



class DeliveryService:
    def __init__(self, session: AsyncSession, redis_url, client_id: str, client_secret: str):
        self.session: AsyncSession = session
        self.token: str = ''
        self.redis = redis.Redis.from_url(redis_url)

        self.client_id = client_id
        self.client_secret = client_secret

    async def get_token(self) -> str:
        token = self.redis.get(self.token).decode()
        if token:
            print('cache token')
            return token

        return await self.update_token()

    async def update_token(self) -> str:
        url = "https://api.cdek.ru/v2/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        async with aiohttp.ClientSession() as http_session:
            async with http_session.post(url, data=data, headers=headers) as response:
                if response.status == 200:
                    json_response = await response.json()
                    access_token = json_response.get("access_token")
                    expires_in = json_response.get("expires_in", 3600)
                    self.redis.set(self.token, access_token, ex=expires_in - 60)
                    return access_token
                else:
                    error_message = await response.text()
                    raise Exception(f"Failed to update token: {response.status} - {error_message}")


    async def get_status(self, order_id: int) -> Product:
        token = await self.get_token()
        url = f"https://api.edu.cdek.ru/v2/orders/{order_id}"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(url, headers=headers) as response:
                if response.status == 200:
                    json_response = await response.json()
                    pprint(json_response)
                    return json_response['entity']['statuses'][0]
                else:
                    error_message = await response.text()
                    raise Exception(f"Failed to update token: {response.status} - {error_message}")

    async def create_order(self, order: Order):
        products = []
        for product in order.products:
            logger.error(product.product_variation.product.title)
            item = {
                "name": f"{product.product_variation.product.title}",
                "ware_key": f"{product.product_variation.uuid_1c}",
                "payment": {
                    "value": product.product_variation.price,
                    # "vat_sum": 0.1,
                    # "vat_rate": 0
                    },
                "cost": product.product_variation.price,
                "weight": 100,
                "amount": product.quantity
            }
            products.append(item)
        payload = {
            "number": f"{order.id}",
            "tariff_code": 139,
            "comment": f"{order.comment}",
            "to_location": {
                "city_uuid": f"{order.city_uuid}",
                "city": f"{order.city}",
                "country_code": f"{order.country_code}",
                "country": "Киргизия",
                "address": f"{order.address}"
            },
            "recipient": {
                "name": f"{order.customer_name}",
                "phones": [
                    {
                        "number": f"{order.customer_phone}"
                    }
                ]
            },
            "packages": [
                {
                    "number": f"{order.id}",
                    "weight": 100,
                    "items": products
                }
            ],
            "from_location": {
                "city_uuid": "b81c6e67-030a-4770-a52b-4a355955c4f3",
                "city": "Бишкек",
                "country_code": "KG",
                "country": "Киргизия",
                "region": "Чуйская область",
                "region_code": 537,
                "address": "Медерова 44/1"
            }
        }
        token = await self.get_token()
        url = "https://api.edu.cdek.ru/v2/orders"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        print(payload)
        async with aiohttp.ClientSession() as http_session:
            async with http_session.post(url, json=payload, headers=headers) as response:
                if response.status == 200 or response.status == 202:
                    json_response = await response.json()
                    logger.info(json_response)

                    order.sdek_id = json_response['entity']['uuid']
                    await self.session.commit()


                else:
                    error_message = await response.text()
                    logger.error(response.json())
                    raise Exception(f"Failed to create sdek delivery: {response.status} - {error_message}")


    async def get_cities(self, name: str, country_code: str = "RU") -> dict:
        token = await self.get_token()
        url = "https://api.edu.cdek.ru/v2/location/suggest/cities"
        print(token)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        params = {
            "name": name,
            "country_code": country_code
        }

        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_message = await response.text()
                    logger.error(f"Failed to fetch cities: {response.status} - {error_message}")
                    raise Exception(f"Failed to fetch cities: {response.status} - {error_message}")
