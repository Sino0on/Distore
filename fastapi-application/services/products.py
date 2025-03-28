from typing import List

from loguru import logger
from sqlalchemy import select, desc, asc, Select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload, aliased, contains_eager, load_only

from api.dependencies.pagination import Pagination
from api.dependencies.product.ordering import Ordering
from core.filters.products import ProductFilter, PropertyFilter
from core.models import Product, Category, CategoryProperty, Brand, User
from core.schemas import PaginationMetadata
from core.models.product import ProductVariation, ProductProperty
from core.schemas.product import ProductPropertiesFilter, ProductResponseWithPagination


class ProductService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_product(self, product_id: int) -> Product:
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(joinedload(Product.brand))
            .options(
                joinedload(Product.category)
                .joinedload(Category.properties)
                .joinedload(CategoryProperty.values)
            )
            .options(
                joinedload(Product.variations).joinedload(ProductVariation.properties)
            )
            .options(joinedload(Product.images))
        )
        result = await self.session.scalar(stmt)

        return result

    @staticmethod
    def _check_variations_filters(product_filter: ProductFilter) -> bool:
        logger.info(
            f"Checking variations filters: {(product_filter.price__gte, product_filter.price__lte, product_filter.properties_list)}"
        )
        if any(
            (
                product_filter.price__gte,
                product_filter.price__lte,
                product_filter.properties_list,
            )
        ):
            logger.info("Variations filters found")
            return True
        return False

    def _filter_products_variations_by_properties(
        self, stmt: Select, properties: List[PropertyFilter]
    ):
        # Если передано несколько свойств, то фильтруем по ним
        for prop in properties:
            stmt = stmt.join(ProductVariation.properties).where(
                ProductProperty.name == prop.name,
                ProductProperty.value == prop.value
            )

        return stmt

    def _filter_products(
        self, product_filter: ProductFilter, properties: List[PropertyFilter] = None
    ):
        # Основной запрос для продуктов с отфильтрованными вариациями
        stmt = (
            select(Product)
            .join(Product.variations)
            .outerjoin(ProductVariation.properties)
            .where(Product.active == True)
        )
        if properties:
            stmt = self._filter_products_variations_by_properties(stmt, properties)

        stmt = self._filter_products_variations(
            product_filter, stmt
        )

        stmt = (
            stmt.outerjoin(Product.brand)
            .join(Product.category)
            .options(
                selectinload(Product.images),
                joinedload(Product.brand),
                joinedload(Product.category),
            )
        )

        if product_filter.brand.name__in:
            logger.info(f"Brand in filter: {product_filter.brand.name__in}")
            stmt = stmt.where(Brand.name.in_(product_filter.brand.name__in))
        if product_filter.category.name__in:
            stmt = stmt.where(Category.name.in_(product_filter.category.name__in))

        if product_filter.search:
            search_term = product_filter.search.strip()
            alternative_term = search_term.replace(" ", "-")

            stmt = stmt.where(
                or_(
                    Product.title.ilike(f"%{search_term}%"),
                    Product.title.ilike(f"%{alternative_term}%")
                )
            )


        return stmt

    async def get_properties(self):
        stmt = select(ProductProperty)
        result = await self.session.execute(stmt)
        result = result.scalars().all()
        return result


    async def get_properties_for_filtered_products(self, product_filter: ProductFilter,
                                                   properties: List[PropertyFilter] = None) -> List[dict]:
        # 1. Фильтрация продуктов (получаем все продукты, соответствующие фильтрам)
        stmt = self._filter_products(product_filter, properties)

        # Выполняем запрос и получаем отфильтрованные продукты
        result = await self.session.execute(stmt)
        products = result.scalars().unique().all()

        # 2. Собираем ID продуктов, чтобы использовать в дальнейшем
        product_ids = [product.id for product in products]

        # 3. Получаем все вариации для этих продуктов
        variations_stmt = (
            select(ProductVariation)
            .join(Product)
            .where(Product.id.in_(product_ids))  # фильтруем по полученным ID продуктов
        )

        variations_result = await self.session.execute(variations_stmt)
        variations = variations_result.scalars().all()

        # 4. Получаем свойства для каждой вариации
        property_stmt = (
            select(ProductProperty)
            .where(ProductProperty.variation_id.in_([v.id for v in variations]))  # фильтруем по вариациям
        )

        properties_result = await self.session.execute(property_stmt)
        product_properties = properties_result.scalars().all()

        # Формируем итоговый список свойств (с ID, name, value)
        properties_list = [
            {"id": prop.id, "name": prop.name, "value": prop.value} for prop in product_properties
        ]

        return properties_list

    @staticmethod
    def _filter_products_variations(
        product_filter: ProductFilter,
        stmt: Select,
    ):

        price_gte = product_filter.price__gte
        price_lte = product_filter.price__lte
        product_filter.price__gte = None
        product_filter.price__lte = None

        # Подзапрос для фильтрации вариаций по цене и свойствам
        variations_query = (
            select(ProductVariation.id)
            .outerjoin(ProductVariation.properties)
            .where(and_(ProductVariation.active == True, ProductVariation.quantity > 0))
        )

        # Фильтрация по цене
        if price_gte is not None:
            variations_query = variations_query.where(
                ProductVariation.price >= price_gte
            )
        if price_lte is not None:
            variations_query = variations_query.where(
                ProductVariation.price <= price_lte
            )

        # # Фильтрация по значениям свойств (properties)
        # aliases = [
        #     {
        #         "alias": aliased(ProductProperty),
        #         "value": value,
        #     }
        #     for value in properties
        # ]
        #
        # for _alias in aliases:
        #     variations_query = variations_query.join(_alias["alias"]).where(
        #         _alias["alias"].value == _alias["value"]
        #     )

        variations_subquery = variations_query.subquery()

        stmt = stmt.where(ProductVariation.id.in_(select(variations_subquery)))

        stmt = stmt.options(
            contains_eager(Product.variations).selectinload(ProductVariation.properties)
        )

        return stmt

    @staticmethod
    def _order_products(order_by: Ordering, stmt: Select):
        order_by_dict = dict()

        if order_by.order_by_price is not None:
            direction = desc if order_by.order_by_price.startswith("-") else asc
            order_by_dict["price"] = direction(ProductVariation.price)

        if order_by.order_by_created_at is not None:
            direction = desc if order_by.order_by_created_at.startswith("-") else asc
            order_by_dict["created_at"] = direction(Product.id)

        order_by_list = [order_by_dict[i.strip(" -")] for i in order_by.order_by_list]

        if order_by_list:
            stmt = stmt.order_by(*order_by_list)

        return stmt

    async def get_products(
        self,
        product_filter: ProductFilter,
        pagination: Pagination,
        order_by: Ordering,
        properties: List[PropertyFilter]
    ):

        logger.info(product_filter)
        logger.info(properties)

        stmt = self._filter_products(product_filter, properties)

        stmt = self._order_products(order_by, stmt)

        pagination_metadata = await self.get_pagination_metadata(stmt, pagination)

        stmt = stmt.offset(pagination.page_size * (pagination.page - 1)).limit(200)

        logger.info(properties)
        if properties or product_filter.category.name__in or product_filter.category.name__in:
            properties = await self.get_properties_for_filtered_products(product_filter, properties)
        # else:
        #     properties = await self.get_properties_for_filtered_products(product_filter)


        result = await self.session.execute(stmt)
        items = result.scalars().unique().fetchmany(pagination.page_size)

        return ProductResponseWithPagination(
            items=items,
            pagination=pagination_metadata,
            properties=properties
        )

    async def get_new_products(self, pagination: Pagination):
        stmt = (
            select(Product)
            .where(
                Product.active == True,
                Product.variations.any(
                    and_(
                        ProductVariation.quantity > 0,
                        ProductVariation.active == True,
                        ProductVariation.price > 0
                    )
                ),
            )
            .order_by(desc(Product.id))
        )

        pagination_metadata = await self.get_pagination_metadata(stmt, pagination)

        stmt = stmt.offset(pagination.page_size * (pagination.page - 1)).limit(pagination.page_size)

        result = await self.session.execute(stmt)
        items = result.scalars().unique().all()

        return ProductResponseWithPagination(
            items=items,
            pagination=pagination_metadata
        )

    async def get_bestselling_products(self, pagination: Pagination):
        stmt = (
            select(
                Product, func.sum(ProductVariation.sale_quantity).label("sales_count")
            )
            .join(ProductVariation, Product.id == ProductVariation.product_id)
            .outerjoin(Product.brand)
            .join(Product.category)
            .options(
                selectinload(Product.images),
                selectinload(Product.brand),
                selectinload(Product.category),
            )
            .where(Product.active == True)
            .group_by(Product.id)
            .order_by(desc("sales_count"))
        )

        pagination_metadata = await self.get_pagination_metadata(stmt, pagination)

        stmt = stmt.offset(pagination.page_size * (pagination.page - 1)).limit(pagination.page_size)

        result = await self.session.execute(stmt)
        items = result.scalars().unique().all()

        return ProductResponseWithPagination(
            items=items,
            pagination=pagination_metadata
        )

    async def get_pagination_metadata(self, stmt: Select, pagination: Pagination):
        # Get the total number of records
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_records_result = await self.session.execute(count_stmt)
        total_records = total_records_result.scalar()

        # Calculate total pages
        total_pages = (
            total_records + pagination.page_size - 1
        ) // pagination.page_size  # ceil division

        # Determine has_next and has_previous
        has_next = pagination.page < total_pages
        has_previous = pagination.page > 1

        return PaginationMetadata(
            total_items=total_records,
            page_size=pagination.page_size,
            current_page=pagination.page,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )

    async def get_favorite_products(self, user: User, pagination: Pagination):
        stmt = (
            select(Product)
            .join(User.favorites)
            .where(User.id == user.id)
        )

        pagination_metadata = await self.get_pagination_metadata(stmt, pagination)

        stmt = stmt.offset(pagination.page_size * (pagination.page - 1)).limit(pagination.page_size)

        result = await self.session.execute(stmt)
        items = result.scalars().unique().all()

        return ProductResponseWithPagination(
            items=items,
            pagination=pagination_metadata,
        )

    async def set_favorite_product(self, user: User, product_id: int):
        product = await self.get_product(product_id)
        user.favorites.append(product)
        await self.session.commit()

    async def unset_favorite_product(self, user: User, product_id: int):
        product = await self.get_product(product_id)

        try:
            user.favorites.remove(product)
            await self.session.commit()
        except ValueError:
            pass
