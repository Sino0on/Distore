from sqladmin import ModelView

from core.models import Product
from core.models.product import ProductImage, ProductVariation, ProductProperty


class ProductAdminMixin:
    category = "product"


class ProductAdmin(ProductAdminMixin, ModelView, model=Product):
    column_list = [
        "id",
        "title",
    ]


class ProductImageAdmin(ProductAdminMixin, ModelView, model=ProductImage):
    column_list = [
        "id",
        "url",
        "product",
    ]


class ProductVariationAdmin(ProductAdminMixin, ModelView, model=ProductVariation):
    column_list = [
        "id",
        "price",
        "quantity",
        "product",
    ]


class ProductPropertyAdmin(ProductAdminMixin, ModelView, model=ProductProperty):
    column_list = [
        "id",
        "name",
        "value",
        "variation.product",
    ]

    name_plural = "Product Properties"
