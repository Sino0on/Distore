from sqladmin import ModelView

from core.models import Category, CategoryProperty, Value


class CategoryAdminMixin:
    category = "category"


class CategoryAdmin(CategoryAdminMixin, ModelView, model=Category):
    column_list = [
        "id",
        "name",
    ]
    name_plural = "Categories"


class CategoryPropertyAdmin(CategoryAdminMixin, ModelView, model=CategoryProperty):
    column_list = [
        "id",
        "name",
        "category",
    ]
    name_plural = "Category Properties"


class CategoryPropertyValueAdmin(CategoryAdminMixin, ModelView, model=Value):
    column_list = [
        "id",
        "value",
        "category_property",
    ]
    name_plural = "Category Property Values"
