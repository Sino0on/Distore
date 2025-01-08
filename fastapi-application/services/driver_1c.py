import asyncio
import json

import aiohttp
import requests
from loguru import logger
from requests import JSONDecodeError
from requests.auth import HTTPBasicAuth
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import Brand, Category, Group, CategoryProperty, Value, Product, Order
from core.models.product import ProductVariation, ProductProperty, ProductImage
from core.schemas.brand import BrandCreate
from core.schemas.category import (
    CategoryCreate,
    GroupCreate,
    CategoryPropertyCreate,
    ValueRead,
)
from core.schemas.product import (
    ProductCreateSchema,
    ProductImageCreateSchema,
    ProductVariationCreateSchema,
    ProductPropertyCreateSchema,
)
from core.schemas.schemas_1c import (
    Product1C,
    Variation1C,
    Property1C,
    Order1C,
    Customer1C,
)


class Driver1C:
    AUTH = HTTPBasicAuth(settings.config_1c.username, settings.config_1c.password)

    @classmethod
    def get_brands(cls):
        response = requests.get(
            url=settings.config_1c.brands_url,
            auth=cls.AUTH,
        )

        if response.status_code != 200:
            logger.exception(
                f"Can't get brands. Error code: {response.status_code}\nMessage: {response.text}"
            )
            raise Exception(
                f"Error code: {response.status_code}\nMessage: {response.text}"
            )

        try:
            data = response.json()
        except JSONDecodeError:
            logger.exception(
                f"Can't parse brands. Error code: {response.status_code}\nMessage: {response.text}"
            )
            raise Exception(
                f"Error code: {response.status_code}\nMessage: {response.text}"
            )

        return data

    @classmethod
    def parse_brands(cls, data):
        if not data:
            return []

        return [
            BrandCreate(
                name=brand["name"],
                image_url=brand["image"],
                uuid_1c=brand["id"],
            )
            for brand in data["data"]
        ]

    @classmethod
    def get_categories(cls):
        response = requests.get(
            url=settings.config_1c.categories_url,
            auth=cls.AUTH,
        )

        if response.status_code != 200:
            logger.exception(
                f"Can't get categories. Error code: {response.status_code}\n"
                f"Message: {response.text}"
            )
            raise Exception(
                f"Error code: {response.status_code}\nMessage: {response.text}"
            )

        try:
            data = response.json()
        except JSONDecodeError:
            logger.exception(
                f"Can't parse categories. Error code: {response.status_code}\n"
                f"Message: {response.text}"
            )
            raise Exception(
                f"Error code: {response.status_code}\nMessage: {response.text}"
            )

        return data

    @classmethod
    def parse_categories(cls, data):
        if not data:
            return []

        result = []

        for group_data in data["data"]:
            if not group_data["name"]:
                continue

            group = GroupCreate(
                name=group_data["name"],
                uuid_1c=group_data["id"],
            )

            categories = []

            for category_data in group_data["subcategories"]:
                category = CategoryCreate(
                    name=category_data["name"],
                    uuid_1c=category_data["id"],
                    properties=[
                        CategoryPropertyCreate(
                            uuid_1c=prop["id"],
                            name=prop["name"],
                            values=[ValueRead(value=value) for value in prop["values"]],
                        )
                        for prop in category_data["properties"]
                    ],
                )

                categories.append(category)

            group.categories = categories

            result.append(group)

        return result

    @classmethod
    def get_products_by_category(cls, category_name: str):
        response = requests.post(
            url=settings.config_1c.products_url,
            json={"category": category_name},
            auth=cls.AUTH,
        )

        if response.status_code != 200:
            raise Exception(
                f"Error code: {response.status_code}\nMessage: {response.text}"
            )

        try:
            data = response.json()
        except JSONDecodeError:
            return dict()

        return data

    @classmethod
    async def fetch_products(cls, session, category_name):
        async with session.post(
            url=settings.config_1c.products_url,
            json={"category": category_name},
            auth=aiohttp.BasicAuth(
                settings.config_1c.username, settings.config_1c.password
            ),
        ) as response:
            if response.status != 200:
                raise logger.info(
                    f"Error code: {response.status}\nMessage: {await response.text()}\n"
                    f"URL: {response.url}\ncategory: {category_name}"
                )
            try:
                data = await response.json()
            except (json.decoder.JSONDecodeError, aiohttp.ContentTypeError):
                return

            return data

    @classmethod
    async def get_products_by_category_list(cls, categories: list):
        async with aiohttp.ClientSession() as session:
            tasks = [
                cls.fetch_products(session, category["name"]) for category in categories
            ]
            responses = await asyncio.gather(*tasks)

        products = [response for response in responses if response]

        return products

    @classmethod
    def parse_products(
        cls,
        data,
        brands_map: dict,
        categories_map: dict,
    ) -> list[ProductCreateSchema]:
        if not data:
            return []

        products = []

        for product_data in data["data"]:
            try:
                brand_id = brands_map[product_data.get("brand", "").lower()]
            except KeyError:
                brand_id = None

            variations = []

            for variation_data in product_data["variations"]:
                try:
                    variation = ProductVariationCreateSchema(
                        uuid_1c=variation_data["code_1c"],
                        name=variation_data["name"],
                        quantity=int(variation_data["quantity"]),
                        price=variation_data["price"],
                        sale_quantity=int(variation_data["salequantity"]),
                        properties=[
                            ProductPropertyCreateSchema(
                                uuid_1c=prop["id"],
                                name=prop["name"],
                                value=prop["value"],
                            )
                            for prop in variation_data["properties"]
                        ],
                    )
                    variations.append(variation)
                except Exception as e:
                    with open("errors.txt", "a", encoding="utf-8") as f:
                        f.write(
                            f"{product_data}\n{variation_data['code_1c']}\n"
                            f"{e}\n\n"
                        )


            product = ProductCreateSchema(
                uuid_1c=product_data["code_1c"],
                title=product_data["title"],
                description=product_data["description"],
                brand_id=brand_id,
                category_id=categories_map[product_data["category"]],
                images=[
                    ProductImageCreateSchema(url=image)
                    for image in product_data["images"]
                ],
                variations=variations,
            )

            products.append(product)

        return products

    def _parse_order(self, order: Order) -> Order1C:
        products = []

        for order_product in order.products:
            products.append(
                Product1C(
                    code_1c=order_product.product_variation.product.uuid_1c,
                    variation_code_1c=order_product.product_variation.uuid_1c,
                    quantity=order_product.quantity,
                    variation=Variation1C(
                        properties=[
                            Property1C(name=prop.name, value=prop.value)
                            for prop in order_product.product_variation.properties
                        ]
                    ),
                )
            )

        order_1c = Order1C(
            order_id=order.id,
            products=products,
            customer=Customer1C(
                name=order.customer_name,
                email=order.customer_email,
                phone=order.customer_phone,
                country=order.country,
                city=order.city,
                address=order.address,
                note=order.comment,
            ),
        )

        return order_1c

    async def create_1c_order(
            self,
            order: Order,
            retries: int = 3,
            retry_delay: int = 5
    ) -> dict:
        order_1c = self._parse_order(order)
        result = None
        async with aiohttp.ClientSession() as session:
            for _ in range(retries):
                async with session.post(
                    settings.config_1c.order_create_url,
                    json=order_1c.model_dump(),
                    auth=aiohttp.BasicAuth(
                        settings.config_1c.username, settings.config_1c.password
                    ),
                ) as response:
                    if not response.status == 200:
                        logger.error(
                            f"Error create order request. "
                            f"Error code: {response.status}\n"
                            f"Message: {await response.text()}"
                        )
                        await asyncio.sleep(retry_delay)
                        logger.info(f"Retrying... ({_ + 1})")
                        continue

                    try:
                        result = await response.json()
                    except json.decoder.JSONDecodeError:
                        logger.error(
                        f"Error create order request. "
                        f"Can't parse response. "
                        f"Error code: {response.status}\n"
                        f"Message: {await response.text()}"
                    )
                    break

        return result

class Saver1C:
    def __init__(self, session):
        self.session: AsyncSession = session

    async def get_brands_map_for_1c(self):
        stmt = select(Brand)
        brands = await self.session.scalars(stmt)
        return {brand.name.lower(): brand.id for brand in brands.all()}

    async def get_categories_map_for_1c(self):
        stmt = select(Category)
        categories = await self.session.scalars(stmt)
        return {category.uuid_1c: category.id for category in categories.all()}

    @staticmethod
    def _change_url_domain(url: str):
        return url.replace("rdp.it-help.kg:34521", "distore.one")

    async def save_brands(self, brands: list[BrandCreate]):
        insert_stmt = insert(Brand).values(
            [
                {
                    "name": brand.name,
                    "uuid_1c": brand.uuid_1c,
                    "image_url": self._change_url_domain(brand.image_url)
                }
                for brand in brands
            ]
        )
        do_update_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["name"],
            set_={
                "uuid_1c": insert_stmt.excluded.uuid_1c,
                "image_url": insert_stmt.excluded.image_url
            },
        )

        await self.session.execute(do_update_stmt)
        await self.session.commit()

    async def save_categories(self, groups: list[GroupCreate]):
        group_insert_stmt = insert(Group).values(
            [
                {
                    "name": group.name,
                    "uuid_1c": group.uuid_1c,
                }
                for group in groups
            ]
        )

        do_update_stmt = group_insert_stmt.on_conflict_do_update(
            index_elements=["uuid_1c"],
            set_={
                "name": group_insert_stmt.excluded.name,
            },
        ).returning(Group.id, Group.uuid_1c)

        group_result = await self.session.execute(do_update_stmt)
        group_mapping = {row.uuid_1c: row.id for row in group_result.fetchall()}

        logger.info(group_mapping)

        category_insert_values = []
        properties = {}
        properties_values = {}

        for group in groups:
            group_id = group_mapping[group.uuid_1c]

            for category in group.categories:
                category_insert_values.append(
                    {
                        "group_id": group_id,
                        "name": category.name,
                        "uuid_1c": category.uuid_1c,
                    }
                )

                properties[category.uuid_1c] = category.properties

                for prop in category.properties:
                    properties_values[prop.uuid_1c] = prop.values

        category_insert_stmt = insert(Category).values(category_insert_values)

        do_update_stmt = category_insert_stmt.on_conflict_do_update(
            index_elements=["uuid_1c"],
            set_={
                "name": category_insert_stmt.excluded.name,
            },
        ).returning(Category.id, Category.uuid_1c)

        category_result = await self.session.execute(do_update_stmt)
        category_mapping = {row.uuid_1c: row.id for row in category_result.fetchall()}

        properties_insert_values = []
        properties_values_insert_values = []

        for key, value in properties.items():
            properties_insert_values.extend(
                [
                    {
                        "category_id": category_mapping[key],
                        "uuid_1c": prop.uuid_1c,
                        "name": prop.name,
                    }
                    for prop in value
                ]
            )

        properties_insert_stmt = insert(CategoryProperty).values(
            properties_insert_values
        )

        do_update_stmt = properties_insert_stmt.on_conflict_do_update(
            index_elements=["uuid_1c"],
            set_={
                "name": properties_insert_stmt.excluded.name,
            },
        ).returning(CategoryProperty.id, CategoryProperty.uuid_1c)

        properties_result = await self.session.execute(do_update_stmt)
        properties_mapping = {
            row.uuid_1c: row.id for row in properties_result.fetchall()
        }

        for key, value in properties_values.items():
            unique_values = set(i.value for i in value)
            properties_values_insert_values.extend(
                [
                    {
                        "category_property_id": properties_mapping[key],
                        "value": i,
                    }
                    for i in unique_values
                ]
            )

        properties_values_insert_stmt = insert(Value).values(
            properties_values_insert_values
        )

        do_update_stmt = properties_values_insert_stmt.on_conflict_do_update(
            constraint="uix_category_property_value",
            set_={
                "value": properties_values_insert_stmt.excluded.value,
            },
        ).returning(Value.id)

        await self.session.execute(do_update_stmt)
        await self.session.commit()

    async def save_products(self, products: list[ProductCreateSchema]):
        variations = {}
        properties = {}
        products_insert_values = []
        properties_ids = []

        for product in products:
            variations[product.uuid_1c] = product.variations

            for variation_ in product.variations:
                properties[variation_.uuid_1c] = variation_.properties

            products_insert_values.append(
                {
                    "title": product.title,
                    "description": product.description,
                    "brand_id": product.brand_id,
                    "category_id": product.category_id,
                    "uuid_1c": product.uuid_1c,
                }
            )
        products_insert_stmt = insert(Product).values(products_insert_values)
        do_update_stmt = products_insert_stmt.on_conflict_do_update(
            index_elements=["uuid_1c"],
            set_={
                "title": products_insert_stmt.excluded.title,
                "description": products_insert_stmt.excluded.description,
                "brand_id": products_insert_stmt.excluded.brand_id,
                "category_id": products_insert_stmt.excluded.category_id,
                "uuid_1c": products_insert_stmt.excluded.uuid_1c,
                "active": True,
            },
        ).returning(Product.id, Product.uuid_1c)

        product_result = await self.session.execute(do_update_stmt)
        product_map = {row.uuid_1c: row.id for row in product_result.fetchall()}

        variations_insert_values = []
        properties_insert_values = []

        for key, value in variations.items():
            variations_insert_values.extend(
                [
                    {
                        "product_id": product_map[key],
                        "uuid_1c": variation_.uuid_1c,
                        "name": variation_.name,
                        "price": variation_.price,
                        "quantity": variation_.quantity,
                        "sale_quantity": variation_.sale_quantity,
                    }
                    for variation_ in value
                ]
            )

        if variations_insert_values:
            variations_insert_stmt = insert(ProductVariation).values(
                variations_insert_values
            )

            variations_do_update_stmt = variations_insert_stmt.on_conflict_do_update(
                index_elements=["uuid_1c"],
                set_={
                    "name": variations_insert_stmt.excluded.name,
                    "price": variations_insert_stmt.excluded.price,
                    "quantity": variations_insert_stmt.excluded.quantity,
                    "sale_quantity": variations_insert_stmt.excluded.sale_quantity,
                },
            ).returning(ProductVariation.id, ProductVariation.uuid_1c)

            variations_result = await self.session.execute(variations_do_update_stmt)
            variations_map = {row.uuid_1c: row.id for row in variations_result.fetchall()}

            for key, value in properties.items():
                properties_insert_values.extend(
                    [
                        {
                            "variation_id": variations_map[key],
                            "name": prop.name,
                            "value": prop.value,
                        }
                        for prop in value
                    ]
                )

            if properties_insert_values:
                # try:
                #     properties_insert_stmt = insert(ProductProperty).values(
                #         properties_insert_values
                #     )
                #
                #     properties_do_update_stmt = properties_insert_stmt.on_conflict_do_update(
                #         constraint="uix_variation_name_value",
                #         set_={
                #             "name": properties_insert_stmt.excluded.name,
                #             "value": properties_insert_stmt.excluded.value,
                #         },
                #     ).returning(ProductProperty.id)
                #
                #     properties_result = await self.session.execute(properties_do_update_stmt)
                #     properties_ids = [row.id for row in properties_result.fetchall()]
                #     properties_batch_save_success = True
                # except Exception as e:
                #     properties_batch_save_success = False
                #     logger.error(f"Error batch saving properties: {e}")

                # if not properties_batch_save_success:
                for key, value in properties.items():
                    properties_insert_values = []
                    for prop in value:
                        properties_insert_values.append(
                            {
                                "variation_id": variations_map[key],
                                "name": prop.name,
                                "value": prop.value,
                            }
                        )
                        property_stmt = insert(ProductProperty).values([{
                                "variation_id": variations_map[key],
                                "name": prop.name,
                                "value": prop.value,
                            }])
                        property_do_update_stmt = property_stmt.on_conflict_do_update(
                            constraint="uix_variation_name_value",
                            set_={
                                "name": property_stmt.excluded.name,
                                "value": property_stmt.excluded.value,
                            },
                        ).returning(ProductProperty.id)
                        property_result = await self.session.execute(
                            property_do_update_stmt
                            )
                        properties_ids.extend([
                            row.id for row in property_result.fetchall()
                        ])

        images_insert_values = []
        for product in products:
            for image in product.images:
                images_insert_values.append(
                    {
                        "product_id": product_map[product.uuid_1c],
                        "url": self._change_url_domain(image.url)
                    }
                )
        logger.info(f"Images insert: {len(images_insert_values)}")
        if images_insert_values:
            images_insert_stmt = insert(ProductImage).values(images_insert_values)

            images_do_update_stmt = images_insert_stmt.on_conflict_do_update(
                constraint="uix_image_product_url",
                set_={
                    "url": images_insert_stmt.excluded.url
                }
            ).returning(ProductImage.id)

            images_result = await self.session.execute(images_do_update_stmt)

        await self.session.commit()

        return properties_ids

    async def delete_old_products(self, products: list[ProductCreateSchema]):
        products_uuids = [product.uuid_1c for product in products]
        products_variations_uuids = []

        for product in products:
            for variation in product.variations:
                products_variations_uuids.append(variation.uuid_1c)

        products_to_delete = await self.session.scalars(
            select(Product).where(Product.uuid_1c.not_in(products_uuids))
        )

        products_to_delete = products_to_delete.all()
        logger.info(len(products_to_delete))

        if products_to_delete:
            for product in products_to_delete:
                await self.session.delete(product)

        await self.session.commit()

        products_variations_to_delete = await self.session.scalars(
            select(ProductVariation).where(
                ProductVariation.uuid_1c.not_in(products_variations_uuids)
            )
        )

        products_variations_to_delete = products_variations_to_delete.all()

        if products_variations_to_delete:
            for variation in products_variations_to_delete:
                await self.session.delete(variation)

        await self.session.commit()

    async def deactivate_old_products(
        self, products: list[ProductCreateSchema], properties_ids: list[int]
    ):
        products_uuids = [product.uuid_1c for product in products]
        products_variations_uuids = []
        image_urls = []

        for product in products:
            for variation in product.variations:
                products_variations_uuids.append(variation.uuid_1c)

            for image in product.images:
                image_urls.append(self._change_url_domain(image.url))

        products_to_deactivate = await self.session.execute(
            update(Product)
            .where(Product.uuid_1c.not_in(products_uuids))
            .values(active=False)
        )

        products_variations_to_deactivate = await self.session.execute(
            update(ProductVariation)
            .where(ProductVariation.uuid_1c.not_in(products_variations_uuids))
            .values(active=False)
        )

        await self.session.commit()

        logger.info(f"Images: {len(image_urls)}")

        images_to_delete = await self.session.execute(
            delete(ProductImage).where(ProductImage.url.not_in(image_urls))
        )

        await self.session.commit()

        properties_to_delete = await self.session.execute(
            delete(ProductProperty).where(ProductProperty.id.not_in(properties_ids))
        )

        await self.session.commit()
