from pydantic import BaseModel

from core.schemas.base import BaseWithORM


class BrandRead(BaseWithORM):
    id: int
    name: str
    image_url: str | None = None


class BrandCreate(BaseModel):
    name: str
    image_url: str | None = None
    uuid_1c: str