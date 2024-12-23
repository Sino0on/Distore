from typing import Sequence

from celery.bin.result import result
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, Address, User
from core.schemas.user import AddressCreate, AddressUpdate


class AddressService:
    def __init__(self, session: AsyncSession, user: User):
        self.session: AsyncSession = session
        self.user: User = user

    async def create_address(self, address_data: AddressCreate) -> Address:
        if self.user.address:
            raise HTTPException(status_code=400, detail="Address already exists")

        address = Address(**address_data.model_dump(), user=self.user)

        self.session.add(address)
        await self.session.commit()
        await self.session.refresh(address)

        return address

    async def get_address_by_user(self) -> Address:
        address = self.user.address

        if not address:
            raise HTTPException(status_code=404, detail="Address not found")

        return address

    async def update_address(self, address_data: AddressUpdate) -> Address:
        address = await self.get_address_by_user()

        address.customer_name = address_data.customer_name or address.customer_name
        address.customer_phone = address_data.customer_phone or address.customer_phone
        address.customer_email = address_data.customer_email or address.customer_email
        address.country = address_data.country or address.country
        address.city = address_data.city or address.city
        address.address = address_data.address or address.address
        address.comment = address_data.comment or address.comment

        await self.session.commit()
        await self.session.refresh(address)

        return address
