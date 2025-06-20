from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins.id_int_pk import IdIntPkMixin

if TYPE_CHECKING:
    from .product import ProductVariation
    from .user import User


class Cart(Base, IdIntPkMixin):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="cart", single_parent=True, lazy="joined")
    products: Mapped[list["CartProduct"]] = relationship(
        back_populates="cart",
        cascade="all, delete",
        lazy="selectin",
        order_by="CartProduct.id",
    )
    total_price: Mapped[int] = mapped_column(default=0)


class CartProduct(Base, IdIntPkMixin):
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    cart: Mapped["Cart"] = relationship(back_populates="products")

    product_variation_id: Mapped[int] = mapped_column(
        ForeignKey("product_variations.id")
    )
    product_variation: Mapped["ProductVariation"] = relationship(
        back_populates="cart_products",
        lazy="joined",
    )

    parent_cart_product_id: Mapped[int | None] = mapped_column(
        ForeignKey("cart_products.id"),
        nullable=True,
    )
    parent: Mapped[Optional["CartProduct"]] = relationship(
        back_populates="children", remote_side="CartProduct.id"
    )
    children: Mapped[list["CartProduct"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    quantity: Mapped[int] = mapped_column(default=1)
