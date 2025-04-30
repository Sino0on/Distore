from typing import TYPE_CHECKING, Optional

from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseUserTable,
    SQLAlchemyUserDatabase,
)
from sqlalchemy import ForeignKey, Table, Column, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.types.user_id import UserIdType
from .base import Base
from .mixins.id_int_pk import IdIntPkMixin

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from .cart import Cart
    from .order import Order


user_favorites = Table(
    "user_favorites",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True),
)


class User(Base, IdIntPkMixin, SQLAlchemyBaseUserTable[UserIdType]):
    name: Mapped[str] = mapped_column(nullable=True)
    nickname: Mapped[str] = mapped_column(unique=True)
    phone_number: Mapped[str]
    address: Mapped[Optional["Address"]] = relationship(back_populates="user", uselist=False, lazy="joined")

    cart: Mapped["Cart"] = relationship(
        back_populates="user",
        cascade="all, delete",
        lazy="joined",
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        lazy="joined",
    )

    favorites: Mapped[list["Product"]] = relationship(
        secondary=user_favorites,
        back_populates="favorited_by",
        lazy="selectin",
    )

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, cls)


class Address(Base, IdIntPkMixin):
    customer_name: Mapped[str]
    customer_phone: Mapped[str]
    customer_email: Mapped[str]
    country: Mapped[str]
    country_code: Mapped[str]
    city: Mapped[str]
    city_uuid: Mapped[str]
    city_code: Mapped[str]
    address: Mapped[str]
    comment: Mapped[str | None] = mapped_column(Text)

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="address", single_parent=True)
