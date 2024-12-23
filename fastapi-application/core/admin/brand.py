from sqladmin import ModelView

from core.models import Brand


class BrandAdmin(ModelView, model=Brand):
    column_list = [
        "id",
        "name",
        "image_url",
    ]
    form_columns = [
        "name",
        "image",
    ]
