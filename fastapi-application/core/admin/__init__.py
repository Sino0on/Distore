from sqladmin import Admin

from core.admin.brand import BrandAdmin
from core.admin.category import CategoryAdmin, CategoryPropertyAdmin, CategoryPropertyValueAdmin
from core.admin.product import ProductAdmin, ProductImageAdmin, ProductVariationAdmin, \
    ProductPropertyAdmin
from core.models import db_helper


def create_admin(app):
    admin = Admin(app, engine=db_helper.engine)
    admin.add_view(BrandAdmin)

    admin.add_view(CategoryAdmin)
    admin.add_view(CategoryPropertyAdmin)
    admin.add_view(CategoryPropertyValueAdmin)

    admin.add_view(ProductAdmin)
    admin.add_view(ProductImageAdmin)
    admin.add_view(ProductVariationAdmin)
    admin.add_view(ProductPropertyAdmin)

    return admin
