from loguru import logger
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from core.models.banner import banner_products, Banner
from core.schemas.banner import *
# from core.models import db_helper, Category, Group, CategoryProperty, Banner


class BannerService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_banners(self):
        stmt = select(Banner).where(Banner.status == True)
        result = await self.session.scalars(stmt)
        logger.info(type(result))
        logger.info(result)
        return result.unique().all()

    async def get_banner(self, banner_id: int) -> Banner:
        stmt = (
            select(Banner)
            .where(Banner.id == banner_id)
        )
        result = await self.session.scalars(stmt)
        logger.info(result)
        return result.first()

    async def create_banner(self, banner_data: BannerCreateSchema) -> Banner:
        # Преобразуем список product_ids в строку для хранения
        product_ids_str = ",".join(map(str, banner_data.product_ids)) if banner_data.product_ids else None

        banner = Banner(
            image=banner_data.image,
            title=banner_data.title,
            title_ky=banner_data.title_ky,
            title_en=banner_data.title_en,
            description=banner_data.description,
            description_ky=banner_data.description_ky,
            description_en=banner_data.description_en,
            product_ids=product_ids_str,
            status=banner_data.status
        )

        self.session.add(banner)
        await self.session.commit()
        await self.session.refresh(banner)

        # Если есть product_ids, добавляем связи в ассоциативную таблицу
        if banner_data.product_ids:
            await self._update_banner_products(banner.id, banner_data.product_ids)

        return banner

    async def update_banner(self, banner_id: int, update_data: BannerUpdateSchema) -> Optional[Banner]:
        banner = await self.get_banner(banner_id)
        if not banner:
            return None

        # Обновляем поля, если они переданы
        if update_data.image is not None:
            banner.image = update_data.image
        if update_data.title is not None:
            banner.title = update_data.title
        if update_data.title_ky is not None:
            banner.title_ky = update_data.title_ky
        if update_data.title_en is not None:
            banner.title_en = update_data.title_en
        if update_data.description is not None:
            banner.description = update_data.description
        if update_data.description_ky is not None:
            banner.description_ky = update_data.description_ky
        if update_data.description_en is not None:
            banner.description_en = update_data.description_en
        if update_data.status is not None:
            banner.status = update_data.status

        # Обновляем product_ids если они переданы
        if update_data.product_ids is not None:
            product_ids_str = ",".join(map(str, update_data.product_ids)) if update_data.product_ids else None
            banner.product_ids = product_ids_str
            await self._update_banner_products(banner_id, update_data.product_ids)

        await self.session.commit()
        await self.session.refresh(banner)
        return banner

    async def delete_banner(self, banner_id: int) -> bool:
        banner = await self.get_banner(banner_id)
        if not banner:
            return False

        # Удаляем связи с продуктами
        await self.session.execute(
            delete(banner_products).where(banner_products.c.banner_id == banner_id)
        )

        # Удаляем сам баннер
        await self.session.delete(banner)
        await self.session.commit()
        return True

    async def _update_banner_products(self, banner_id: int, product_ids: List[int]) -> None:
        # Сначала удаляем все существующие связи для этого баннера
        await self.session.execute(
            delete(banner_products).where(banner_products.c.banner_id == banner_id)
        )

        # Затем добавляем новые связи
        for product_id in product_ids:
            await self.session.execute(
                banner_products.insert().values(banner_id=banner_id, product_id=product_id)
            )

        await self.session.commit()
