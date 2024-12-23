from typing import Optional

from fastapi_storages.integrations.sqlalchemy import FileType, ImageType
from sqlalchemy import Column
from sqlalchemy.orm import Mapped, mapped_column, relationship


from .base import Base
from .mixins.id_int_pk import IdIntPkMixin
from ..config import settings


class Brand(Base, IdIntPkMixin):
    name: Mapped[str] = mapped_column(unique=True)
    image_url: Mapped[str]
    uuid_1c: Mapped[str] = mapped_column(unique=True)

    products: Mapped[list["Product"]] = relationship(
        back_populates="brand",
        cascade="all, delete",
    )

    def __repr__(self):
        return self.name
