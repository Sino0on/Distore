import asyncio
from datetime import datetime

from loguru import logger

from core.models import db_helper
from services.driver_1c import Driver1C, Saver1C


async def save_brands():
    brands = Driver1C.parse_brands(Driver1C.get_brands())

    async with db_helper.session_factory() as session:
        saver = Saver1C(session)

        await saver.save_brands(brands)

async def save_categories():
    categories = Driver1C.parse_categories(Driver1C.get_categories())

    async with db_helper.session_factory() as session:
        saver = Saver1C(session)

        await saver.save_categories(categories)


async def get_parse_products():
    async with db_helper.session_factory() as session:
        saver = Saver1C(session)

        print(datetime.utcnow())

        brand_map = await saver.get_brands_map_for_1c()
        category_map = await saver.get_categories_map_for_1c()

        print(datetime.utcnow())

        categories = Driver1C.get_categories()
        products_responses = await Driver1C.get_products_by_category_list(
            categories["data"]
        )

        print(datetime.utcnow())

        products = []

        for response in products_responses:
            products.extend(Driver1C.parse_products(response, brand_map, category_map))

        print(datetime.utcnow())
        logger.info(f'Products count: {len(products)}')

        return products

async def save_products():
    products = await get_parse_products()

    async with db_helper.session_factory() as session:
        saver = Saver1C(session)

        start_time = datetime.utcnow()
        logger.info(f"start save products: {start_time} | {len(products)}")

        properties_ids = []
        chunk_size = 50

        for num, chunk in enumerate(
            [
                products[i : i + chunk_size]
                for i in range(0, len(products), chunk_size)
            ]
        ):
            logger.info(f"chunk: {num} start | {datetime.utcnow()}")
            properties_ids.extend(await saver.save_products(chunk))
            logger.info(f"chunk: {num} end | {datetime.utcnow()}")

        end_time = datetime.utcnow()
        logger.info(f"end save products: {end_time}")

        await saver.deactivate_old_products(products, properties_ids)

        logger.info(f"start time: {start_time} | end time: {datetime.utcnow()}")
        print(datetime.utcnow())


async def delete_products(products):
    async with db_helper.session_factory() as session:
        saver = Saver1C(session)

        await saver.delete_old_products(products)


async def main():
    while True:
        try:
            await save_brands()
        except Exception as e:
            logger.exception(e)

        try:
            await save_categories()
        except Exception as e:
            logger.exception(e)

        try:
            await save_products()
        except Exception as e:
            logger.exception(e)

        await asyncio.sleep(60 * 5)


if __name__ == "__main__":
    asyncio.run(main())

