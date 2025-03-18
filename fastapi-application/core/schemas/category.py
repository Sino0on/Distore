from pydantic import BaseModel


class ValueRead(BaseModel):
    value: str


class CategoryPropertyRead(BaseModel):
    name: str
    values: list[ValueRead]


class CategoryRead(BaseModel):
    id: int
    name: str
    name_ky: str
    name_en: str
    properties: list[CategoryPropertyRead]


class GroupRead(BaseModel):
    id: int
    name: str
    name_ky: str
    name_en: str
    categories: list[CategoryRead]


class CategoryPropertyCreate(CategoryPropertyRead):
    uuid_1c: str
    name: str

    values: list[ValueRead]


class CategoryCreate(BaseModel):
    name: str
    uuid_1c: str

    properties: list[CategoryPropertyCreate] | None = None


class GroupCreate(BaseModel):
    name: str
    uuid_1c: str

    categories: list[CategoryCreate] | None = None
