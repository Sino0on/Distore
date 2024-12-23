from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins.id_int_pk import IdIntPkMixin
from .user import user_favorites

if TYPE_CHECKING:
    from .user import User
    from .brand import Brand
    from .category import Category
    from .cart import CartProduct
    from .order import OrderProduct


class Product(Base, IdIntPkMixin):
    __tablename__ = "products"

    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(Text)
    uuid_1c: Mapped[str] = mapped_column(unique=True)

    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"), nullable=True)
    brand: Mapped["Brand"] = relationship(back_populates="products", lazy="joined")

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="products", lazy="joined")

    created_at = mapped_column(DateTime, default=lambda: datetime.utcnow())
    updated_at = mapped_column(
        DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow()
    )
    active: Mapped[bool] = mapped_column(default=True)

    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete",
        lazy="selectin",
    )

    variations: Mapped[list["ProductVariation"]] = relationship(
        back_populates="product",
        cascade="all, delete",
        lazy="selectin",
    )

    favorited_by: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_favorites,
        back_populates="favorites",
        lazy="selectin",
    )

    def __repr__(self):
        return self.title


class ProductImage(Base, IdIntPkMixin):
    __tablename__ = "product_images"

    url: Mapped[str]

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped["Product"] = relationship(back_populates="images")

    __table_args__ = (
        UniqueConstraint("product_id", "url", name="uix_image_product_url"),
    )

    def __repr__(self):
        return self.url


class ProductVariation(Base, IdIntPkMixin):
    __tablename__ = "product_variations"

    name: Mapped[str]
    price: Mapped[float]
    quantity: Mapped[int]
    sale_quantity: Mapped[int] = mapped_column(default=0)

    uuid_1c: Mapped[str] = mapped_column(unique=True)
    active: Mapped[bool] = mapped_column(default=True)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped["Product"] = relationship(back_populates="variations", lazy="joined")

    properties: Mapped[list["ProductProperty"]] = relationship(
        back_populates="variation",
        cascade="all, delete",
        lazy="selectin",
    )

    cart_products: Mapped[list["CartProduct"]] = relationship(
        back_populates="product_variation",
        cascade="all, delete",
        lazy="selectin"
    )

    order_products: Mapped[list["OrderProduct"]] = relationship(
        back_populates="product_variation",
        lazy="selectin"
    )

    def __repr__(self):
        return f"Product: {self.product_id}: {self.price}"


class ProductProperty(Base, IdIntPkMixin):
    __tablename__ = "product_properties"

    name: Mapped[str]
    value: Mapped[str]

    variation_id: Mapped[int] = mapped_column(ForeignKey("product_variations.id"))
    variation: Mapped["ProductVariation"] = relationship(back_populates="properties")

    __table_args__ = (
        UniqueConstraint("variation_id", "name", "value", name="uix_variation_name_value"),
    )

    def __repr__(self):
        return f"{self.name}: {self.value} | variation: {self.variation_id}"
