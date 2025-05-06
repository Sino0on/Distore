from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqladmin import ModelView
from wtforms import TextAreaField
from core.models import Banner, Product
from sqlalchemy.orm import object_session
from sqlalchemy.future import select


class BannerAdmin(ModelView, model=Banner):
    column_list = ["id", "title", "created_at"]
    form_columns = ["title", "title_ky", "title_en", "description", "description_ky", "description_en", "image", "product_ids", 'status']

    form_extra_fields = {
        "product_ids": TextAreaField("Product IDs (comma-separated)")
    }

    async def on_model_change(self, data, model: Banner, is_created: bool, request: Request):
        # Получаем product_ids из формы
        product_ids_raw = data.pop("product_ids", "")
        id_list = [int(pid.strip()) for pid in product_ids_raw.split(",") if pid.strip().isdigit()]

        # Используем сессию, к которой уже прикреплён model
        session: AsyncSession = object_session(model)

        # Если object_session вернул None (вдруг), fallback на state.session
        if session is None:
            session = request.state.session

        # Загружаем продукты
        result = await session.execute(select(Product).where(Product.id.in_(id_list)))
        products = result.scalars().all()

        # Привязываем продукты к баннеру
        model.products = products
