from fastapi_users import schemas
from pydantic import BaseModel, ConfigDict

from core.types.user_id import UserIdType


class UserRead(schemas.BaseUser[UserIdType]):
    name: str | None = None
    nickname: str
    phone_number: str


class UserCreate(schemas.BaseUserCreate):
    nickname: str
    phone_number: str


class UserUpdate(schemas.BaseUserUpdate):
    name: str | None = None
    nickname: str
    phone_number: str


class AddressCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: str
    country: str
    city: str
    address: str
    comment: str | None = None

    class Config:
        from_attributes = True


class AddressUpdate(BaseModel):
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    country: str | None = None
    city: str | None = None
    address: str | None = None
    comment: str | None = None

    class Config:
        from_attributes = True


class AddressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    customer_phone: str
    customer_email: str
    country: str
    city: str
    address: str
    comment: str | None = None
