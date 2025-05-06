from datetime import datetime
from typing import TYPE_CHECKING, Optional

from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseUserTable,
    SQLAlchemyUserDatabase,
)
from sqlalchemy import ForeignKey, Table, Column, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.types.user_id import UserIdType
from .base import Base
from .mixins.id_int_pk import IdIntPkMixin

if TYPE_CHECKING:
    from .product import Product

banner_products = Table(
    "banner_products",
    Base.metadata,
    Column("banner_id", ForeignKey("banners.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True)
)



class Banner(Base, IdIntPkMixin):
    __tablename__ = "banners"

    image: Mapped[str]  # путь или URL до изображения
    title: Mapped[str]
    title_ky: Mapped[str | None] = mapped_column(Text, nullable=True)
    title_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str]
    description_ky: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.utcnow())

    products: Mapped[list["Product"]] = relationship(
        "Product",
        secondary=banner_products,
        back_populates="banners",
        lazy="selectin"
    )
    product_ids: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True)

