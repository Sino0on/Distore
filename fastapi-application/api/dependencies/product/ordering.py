from typing import Optional

from fastapi import Query, HTTPException
from pydantic import BaseModel, field_validator, Field


class Ordering(BaseModel):
    order_by: Optional[str] = Field(Query(
        None,
        examples=[
            {
                "order_by": "price",
            },
            {
                "order_by": "created_at,-price",
            },
        ],
        description="Ordering fields: `price`, `created_at`\nExample: `price` or `created_at,-price`",
    ))

    @field_validator("order_by")
    @classmethod
    def restrict_sortable_fields(cls, value):
        if value is None:
            return None

        allowed_field_names = ["price", "created_at"]

        values = value.split(",")

        for field_name in values:
            field_name = field_name.replace("+", "").replace("-", "").strip()
            if field_name not in allowed_field_names:
                raise HTTPException(
                    status_code=400,
                    detail=f"You may only sort by: {', '.join(allowed_field_names)}"
                )

        return value

    @property
    def order_by_list(self):
        if self.order_by is None:
            return []
        return self.order_by.split(",")

    @property
    def order_by_price(self):
        price = None
        for value in self.order_by_list:
            field_name = value.replace("+", "").replace("-", "").strip()

            if field_name == "price":
                price = value.strip()

        return price
        # if price is None:
        #     return None
        #
        # if price.startswith("-"):
        #     return desc(ProductVariation.price)
        # else:
        #     return asc(ProductVariation.price)

    @property
    def order_by_created_at(self):
        created_at = None
        for value in self.order_by_list:
            field_name = value.replace("+", "").replace("-", "").strip()

            if field_name == "created_at":
                created_at = value.strip()

        return created_at
        # if created_at is None:
        #     return None
        #
        # if created_at.startswith("-"):
        #     return desc(Product.created_at)
        # else:
        #     return asc(Product.created_at)
