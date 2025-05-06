from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqladmin import ModelView
from wtforms import TextAreaField
from core.models import Banner, Product
from sqlalchemy.future import select
from sqlalchemy.orm.session import object_session


class BannerAdmin(ModelView, model=Banner):
    column_list = ["id", "title", "created_at"]
    form_columns = ["title", "title_ky", "title_en", "description", "description_ky", "description_en", "image", "product_ids", 'status']  # Убедись, что это поле в списке

    form_extra_fields = {
        "product_ids": TextAreaField("Product IDs (comma-separated)")
    }

    async def on_model_change(self, data, model, is_created, request: Request):
        session: AsyncSession = request.state.session

        product_ids_raw = data.pop("product_ids", "")
        id_list = [int(pid.strip()) for pid in product_ids_raw.split(",") if pid.strip().isdigit()]

        # Получаем текущую сессию, к которой привязан model (если есть)
        model_session = object_session(model)

        # Если сессии разные, "сливаем" model в текущую
        if model_session is not session.sync_session:
            model = await session.merge(model)

        result = await session.execute(
            select(Product).where(Product.id.in_(id_list))
        )
        products = result.scalars().all()

        model.products = products