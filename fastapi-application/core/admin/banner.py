from typing import Annotated
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqladmin import ModelView
from wtforms import TextAreaField
from core.models import Banner, Product, db_helper
from sqlalchemy.future import select
from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker


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

    async def on_model_change(
            self,
            data: dict,
            model: Banner,
            is_created: bool,
            request: Request,
            ):
        # Обрабатываем product_ids
        async with async_sessionmaker() as session:
            product_ids_raw = data.get("product_ids", "")

            # Преобразуем строку в список ID
            id_list = []
            if product_ids_raw:
                id_list = [
                    int(pid.strip())
                    for pid in product_ids_raw.split(",")
                    if pid.strip().isdigit()
                ]

            # Получаем продукты из базы
            result = await session.execute(
                select(Product).where(Product.id.in_(id_list))
            )
            products = result.scalars().all()

            # Устанавливаем связь с продуктами
            model.products = products

            # Продолжаем стандартную обработку
            await super().on_model_change(data, model, is_created, request)