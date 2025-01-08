from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins.id_int_pk import IdIntPkMixin


class Group(Base, IdIntPkMixin):
    __tablename__ = "groups"

    name: Mapped[str]
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    uuid_1c: Mapped[str] = mapped_column(unique=True)

    categories: Mapped[list["Category"]] = relationship(
        back_populates="group",
        cascade="all, delete",
    )

    def __repr__(self):
        return self.name


class Category(Base, IdIntPkMixin):
    __tablename__ = "categories"

    name: Mapped[str]
    uuid_1c: Mapped[str] = mapped_column(unique=True)

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    group: Mapped[Group] = relationship()

    properties: Mapped[list["CategoryProperty"]] = relationship(
        back_populates="category",
        cascade="all, delete",
    )
    products: Mapped[list["Product"]] = relationship(
        back_populates="category",
        cascade="all, delete",
    )

    def __repr__(self):
        return self.name


class CategoryProperty(Base, IdIntPkMixin):
    __tablename__ = "category_properties"

    name: Mapped[str]
    uuid_1c: Mapped[str] = mapped_column(unique=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped[Category] = relationship(back_populates="properties")
    values: Mapped[list["Value"]] = relationship(
        back_populates="category_property", cascade="all, " "delete"
    )

    def __repr__(self):
        return f"category: {self.category_id}, property: {self.name}, id: {self.id}"


class Value(Base, IdIntPkMixin):
    __tablename__ = "values"

    value: Mapped[str]

    category_property_id: Mapped[int] = mapped_column(
        ForeignKey("category_properties.id")
    )
    category_property: Mapped[CategoryProperty] = relationship(back_populates="values")

    __table_args__ = (
        UniqueConstraint("category_property_id", "value", name="uix_category_property_value"),
    )

    def __repr__(self):
        return f"value: {self.value}, id: {self.id}, property: {self.category_property_id}"
