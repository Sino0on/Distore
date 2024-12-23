from pydantic import BaseModel


class BaseWithORM(BaseModel):
    class Config:
        from_attributes = True


class PaginationMetadata(BaseModel):
    total_items: int
    page_size: int
    current_page: int
    total_pages: int
    has_next: bool
    has_previous: bool