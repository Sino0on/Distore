from typing import Type, Sequence

from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import User, Order, Address
from core.models.order import OrderProduct, OrderStatus
from core.schemas.order import OrderCreate, OrderUDSDiscountSchema
from core.schemas.user import AddressRead
from services.carts import CartService
from services.mixins.calculate_total_price import CalculateTotalPriceMixin
from services.uds import UDSService


class OrderService(CalculateTotalPriceMixin):
    def __init__(self, session):
        self.session: AsyncSession = session
        self.cart_service = CartService(session)

    async def create_order_from_cart(
        self, user: User, order_data: OrderCreate
    ) -> Order:
        cart = user.cart

        if await self.cart_service.cart_is_empty(cart):
            raise HTTPException(status_code=400, detail="Cart is empty")

        if order_data.use_saved_address:
            address = user.address

            if not user.address:
                raise HTTPException(
                    status_code=404, detail="The user does not have a saved address"
                )

            address_data = AddressRead.model_validate(address).model_dump(
                exclude={"id"}
            )
        else:
            address_data = order_data.model_dump(exclude={"use_saved_address"})

        order = Order(
            user=user,
            total_price=cart.total_price,
            final_price=cart.total_price,
            **address_data
        )

        for cart_product in cart.products:
            order.products.append(
                OrderProduct(
                    order=order,
                    product_variation=cart_product.product_variation,
                    quantity=cart_product.quantity,
                )
            )

        self.session.add_all([order, *order.products])
        await self.session.commit()

        await self.session.refresh(order)

        total_price = await self.calculate_total_price(cart)

        order.total_price = total_price
        order.final_price = total_price

        await self.session.commit()

        await self.cart_service.clear_cart(user)

        return order

    async def _get_order(self, order_id: int) -> Type[Order]:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.products)
                .selectinload(OrderProduct.product_variation)
            )
        )
        result = await self.session.scalar(stmt)

        if not result:
            raise HTTPException(status_code=404, detail="Order not found")

        return result

    async def get_order(self, user: User, order_id: int) -> Type[Order]:
        order = await self._get_order(order_id)

        if order.user_id == user.id or user.is_superuser:
            return order

        raise HTTPException(
            status_code=403,
            detail="You don't have permission to see this order",
        )

    async def delete_order(self, user: User, order_id: int):
        order = await self.get_order(user, order_id)
        await self.session.delete(order)
        await self.session.commit()

    async def get_orders(self, user: User) -> Sequence[Order]:
        stmt = select(Order).where(Order.user_id == user.id)
        result = await self.session.scalars(stmt)

        return result.all()

    async def get_order_products_by_user(self, user: User) -> Sequence[OrderProduct]:
        orders = user.orders
        result = await self.session.scalars(
            select(OrderProduct).where(
                OrderProduct.order_id.in_(order.id for order in orders)
            )
        )

        return result.unique().all()

    async def set_order_uds_discount(
        self,
        user: User,
        discount_data: OrderUDSDiscountSchema,
    ) -> Type[Order]:
        uds_service = UDSService(self.session, user)

        order = await self.get_order(user, discount_data.order_id)

        transaction_data = await uds_service.create_transaction(
            uds_code=discount_data.uds_code,
            total_price=order.total_price,
            points=discount_data.points,
        )

        order.discount = discount_data.points
        order.final_price = order.total_price - discount_data.points
        order.uds_transaction_id = transaction_data.id
        await self.session.commit()
        await self.session.refresh(order)

        return order

    async def set_order_delivery(
        self, user: User, order_id: int, delivery: bool
    ) -> Type[Order]:
        order = await self.get_order(user, order_id)
        order.delivery = delivery
        await self.session.commit()

        return order

    async def payment_update(
        self, order_id: int, status: OrderStatus, payment_data: dict = None
    ):
        order = await self._get_order(order_id)
        is_new_order = False

        if order.status == OrderStatus.paid:
            if order.payment_data:
                old_data = order.payment_data
                old_data["data"].append(payment_data)
                new_data = old_data
                order.payment_data = new_data
            else:
                order.payment_data = {"data": [payment_data]}
        else:
            if order.status not in (OrderStatus.canceled, OrderStatus.error):
                is_new_order = True

            if payment_data:
                order.payment_data = {"data": [payment_data]}

            order.status = status

        await self.session.commit()
        await self.session.refresh(order)

        return order, is_new_order

    async def update_payment_response(
        self,
        response_text: str,
        order_id: int
    ):
        order = await self._get_order(order_id)

        if order.payment_responses:
            old_data = order.payment_responses
            old_data["data"].append(response_text)
            new_data = old_data
            order.payment_responses = new_data
        else:
            order.payment_responses = {"data": [response_text]}

        await self.session.commit()
        await self.session.refresh(order)

        return order


    async def update_order_code_1c(self, order_id: int, code_1c: str):
        order = await self._get_order(order_id)
        order.code_1c = code_1c
        await self.session.commit()
        await self.session.refresh(order)

        return order

    def handle_address_for_order(self, order_data: OrderCreate, user: User):
        # Предположим что у пользователя может быть только один адрес
        if not user.address:
            # Адреса ещё нет — создаем
            new_address = Address(
                user_id=user.id,
                customer_name=order_data.customer_name,
                customer_phone=order_data.customer_phone,
                customer_email=order_data.customer_email,
                country=order_data.country,
                country_code=order_data.country_code,
                city=order_data.city,
                city_uuid=order_data.city_uuid,
                city_code=order_data.city_code,
                address=order_data.address,
                comment=order_data.comment,
            )
            self.session.add(new_address)
        elif not self.addresses_equal(order_data, user.address):
            # Если есть, но отличается — обновляем
            self.update_address(user.address, order_data)

        # В любом случае коммит нужно будет сделать потом

    def addresses_equal(self, order_data: OrderCreate, address: Address) -> bool:
        return (
                order_data.customer_name == address.customer_name and
                order_data.customer_phone == address.customer_phone and
                order_data.customer_email == address.customer_email and
                order_data.country == address.country and
                order_data.country_code == address.country_code and
                order_data.city == address.city and
                order_data.city_uuid == address.city_uuid and
                order_data.city_code == address.city_code and
                order_data.address == address.address and
                order_data.comment == address.comment
        )

    def update_address(self, address: Address, order_data: OrderCreate):
        address.customer_name = order_data.customer_name
        address.customer_phone = order_data.customer_phone
        address.customer_email = order_data.customer_email
        address.country = order_data.country
        address.country_code = order_data.country_code
        address.city = order_data.city
        address.city_uuid = order_data.city_uuid
        address.city_code = order_data.city_code
        address.address = order_data.address
        address.comment = order_data.comment
