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

    async def on_model_change(self, data, model, is_created, request: Request):
        async_session: AsyncSession = request.state.session

        product_ids_raw = data.pop("product_ids", "")
        id_list = [int(pid.strip()) for pid in product_ids_raw.split(",") if pid.strip().isdigit()]

        async def load_products(session: AsyncSession):
            result = await session.execute(
                select(Product).where(Product.id.in_(id_list))
            )
            return result.scalars().all()

        products = await async_session.run_sync(lambda sync_session: sync_session.execute(
            select(Product).where(Product.id.in_(id_list))
        ))  # <-- не сработает напрямую, нужен sync-контекст

        # или же:
        products = await load_products(async_session)

        model.products = products
