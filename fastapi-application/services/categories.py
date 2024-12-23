from fastapi import Depends
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.models import db_helper, Category, Group, CategoryProperty


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_categories(self):
        stmt = select(Group).options(
            joinedload(Group.categories)
            .joinedload(Category.properties)
            .joinedload(CategoryProperty.values)
        )
        result = await self.session.scalars(stmt)
        logger.info(type(result))
        logger.info(result)
        return result.unique().all()

    async def get_category(self, category_id: int) -> Category:
        stmt = (
            select(Category)
            .where(Category.id == category_id)
            .options(
                joinedload(Category.properties).joinedload(CategoryProperty.values)
            )
        )
        result = await self.session.scalars(stmt)
        logger.info(result)
        return result.first()
