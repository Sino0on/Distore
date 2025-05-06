from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins.id_int_pk import IdIntPkMixin
from .user import user_favorites
from .banner import banner_products

if TYPE_CHECKING:
    from .user import User
    from .brand import Brand
    from .category import Category
    from .cart import CartProduct
    from .order import OrderProduct
    from .banner import Banner


class Product(Base, IdIntPkMixin):
    __tablename__ = "products"

    title: Mapped[str]
    title_ky: Mapped[str] = mapped_column(nullable=True)
    title_en: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(Text)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_ky: Mapped[str | None] = mapped_column(Text, nullable=True)
    usingmethod: Mapped[str | None] = mapped_column(Text, nullable=True)
    composition: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    banners: Mapped[list["Banner"]] = relationship(
        "Banner",
        secondary=banner_products,
        back_populates="products",
        lazy="selectin"
    )


    @property
    def main_image(self) -> "ProductImage | None":
        """
        Возвращает главное изображение продукта,
        если оно есть, иначе первое изображение или None.
        """
        return next(
            (img for img in self.images if img.is_main),
            self.images[0] if self.images else None
            )

    def __repr__(self):
        return self.title


class ProductImage(Base, IdIntPkMixin):
    __tablename__ = "product_images"

    url: Mapped[str]
    is_main: Mapped[bool] = mapped_column(default=False)

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

    images: Mapped[list["ProductVariationImage"]] = relationship(
        back_populates="variation",
        cascade="all, delete",
        lazy="selectin",
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


class ProductVariationImage(Base, IdIntPkMixin):
    __tablename__ = "product_variation_images"

    url: Mapped[str]
    is_main: Mapped[bool] = mapped_column(default=False)

    variation_id: Mapped[int] = mapped_column(
        ForeignKey("product_variations.id")
    )
    variation: Mapped["ProductVariation"] = relationship(
        back_populates="images"
    )

    __table_args__ = (
        UniqueConstraint(
            "variation_id", "url",
            name="uix_image_product_variation_url",
        ),
    )

    def __repr__(self):
        return self.url