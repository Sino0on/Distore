import enum
from datetime import datetime
from typing import TYPE_CHECKING

from pygments.lexer import default
from sqlalchemy import ForeignKey, Text, Enum, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base
from core.models.mixins.id_int_pk import IdIntPkMixin

if TYPE_CHECKING:
    from .user import User
    from .product import ProductVariation


class OrderStatus(str, enum.Enum):
    created = "created"
    in_progress = "in_progress"
    completed = "completed"
    canceled = "canceled"
    paid = "paid"
    error = "error"


class Order(Base, IdIntPkMixin):
    customer_name: Mapped[str]
    customer_phone: Mapped[str]
    customer_email: Mapped[str]
    country: Mapped[str]
    city: Mapped[str]
    address: Mapped[str]
    comment: Mapped[str | None] = mapped_column(Text)
    status: Mapped[OrderStatus] = mapped_column(
        # Enum(OrderStatus, name="order_status", create_type=False),
        default=OrderStatus.created,
    )
    total_price: Mapped[float]
    promo_code: Mapped[str | None]
    code_1c: Mapped[str | None]
    delivery: Mapped[bool] = mapped_column(default=True)
    discount: Mapped[int] = mapped_column(default=0)
    final_price: Mapped[float]
    uds_transaction_id: Mapped[int | None] = mapped_column(default=None)
    payment_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at = mapped_column(DateTime, default=lambda: datetime.utcnow())
    updated_at = mapped_column(
        DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow()
    )


    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="orders", lazy="joined")

    products: Mapped[list["OrderProduct"]] = relationship(
        back_populates="order", cascade="all, delete", lazy="selectin"
    )


class OrderProduct(Base, IdIntPkMixin):
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    order: Mapped["Order"] = relationship(back_populates="products", lazy="joined")

    product_variation_id: Mapped[int] = mapped_column(
        ForeignKey("product_variations.id")
    )
    product_variation: Mapped["ProductVariation"] = relationship(
        back_populates="order_products",
        lazy="joined",
    )

    quantity: Mapped[int] = mapped_column(default=1)
