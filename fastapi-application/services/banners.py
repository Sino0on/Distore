from fastapi import Depends
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.models import db_helper, Category, Group, CategoryProperty, Banner


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
