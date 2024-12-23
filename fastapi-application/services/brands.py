from typing import Sequence

from celery.bin.result import result
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, Brand


class BrandService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_all_brands(self) -> Sequence[Brand]:
        stmt = select(Brand)
        items = await self.session.scalars(stmt)

        return items.all()

    async def get_random_brands_list(self, count: int) -> Sequence[Brand]:
        stmt = select(Brand).order_by(func.random()).limit(count)
        items = await self.session.scalars(stmt)

        return items.all()
