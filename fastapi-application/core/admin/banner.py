from typing import Annotated
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqladmin import ModelView
from wtforms import TextAreaField
from core.models import Banner, Product, db_helper
from sqlalchemy.future import select
from fastapi import Depends
from sqlalchemy.orm import Session


class BannerAdmin(ModelView, model=Banner):
    column_list = ["id", "title", "created_at"]
    form_columns = [
        "title", "title_ky", "title_en",
        "description", "description_ky", "description_en",
        "image", "product_ids", "status"
    ]

    form_extra_fields = {
        "product_ids": TextAreaField("Product IDs (comma-separated)")
    }

    def get_session(self, request: Request) -> AsyncSession:
        return request.state.session

    async def on_model_change(self, data: dict, model: Banner, is_created: bool, request: Request):
        session = self.get_session(request)

        # Обработка product_ids
        product_ids_raw = data.get("product_ids", "")
        product_ids = [
            int(pid.strip())
            for pid in product_ids_raw.split(",")
            if pid.strip().isdigit()
        ] if product_ids_raw else []

        # Получаем продукты с учетом текущей сессии
        if product_ids:
            # Вариант 1: Делаем запрос с учетом текущей сессии
            existing_products = []
            for pid in product_ids:
                product = await session.get(Product, pid)
                if product:
                    existing_products.append(product)

            # Вариант 2: Альтернативный способ с merge
            # result = await session.execute(select(Product).where(Product.id.in_(product_ids)))
            # existing_products = []
            # for product in result.scalars():
            #     existing_products.append(await session.merge(product))

            model.products = existing_products
        else:
            model.products = []

        # Вызываем родительский метод
        await super().on_model_change(data, model, is_created, request)