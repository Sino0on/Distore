from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, case
from core.models import Group, Category, CategoryProperty, db_helper, Product  # Импортируем модели из твоего проекта
from googletrans import Translator
from loguru import logger


class Translater:
    def __init__(self):
        self.translator = Translator()

    async def update_translations(self):
        models = [Group, Category]

        async with db_helper.session_factory() as session:
            # for model in models:
            #     stmt = select(model).where(model.name_ky.is_(None) | model.name_en.is_(None))
            #     result = await session.execute(stmt)
            #     records = result.scalars().all()
            #
            #     for record in records:
            #         translations = await self.translate_text(record.name)
            #         record.name_ky = translations["ky"]
            #         record.name_en = translations["en"]
            #
            #     await session.commit()
            #
            stmt = select(Product).where(Product.title_ky.is_(None) | Product.title_en.is_(None) | Product.description_ky.is_(None) | Product.description_en.is_(None))
            result = await session.execute(stmt)
            records = result.scalars().all()

            for record in records:
                try:
                    translations = await self.translate_text(record.title)
                    translations_desc = await self.translate_text(record.description)
                    record.title_ky = translations["ky"]
                    record.title_en = translations["en"]
                    record.description_en = translations_desc["en"]
                    record.description_ky = translations_desc["ky"]
                except:
                    pass

            await session.commit()

    async def translate_text(self, text: str):
        ky = await self.translator.translate(text, src="ru", dest="ky")
        en = await self.translator.translate(text, src="ru", dest="en")
        translations = {
            "ky": ky.text,
            "en": en.text
        }
        logger.info(f"Translate text: {text} to {ky.text}")
        return translations

    async def test_select(self, lang: str = 'ru'):
        async with db_helper.session_factory() as session:
            stmt = select(
                Group).options(
                case(
                    (lang == "ky", Group.name_ky),
                    (lang == "en", Group.name_en),
                    else_=Group.name
                ).label("name")
            )

            result = await session.execute(stmt)
            rows = result.mappings().all()  # Преобразуем в список словарей

            logger.info(f"Тип результата: {type(rows)}")
            logger.info(rows)
