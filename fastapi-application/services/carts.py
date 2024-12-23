from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Cart, User
from core.models.cart import CartProduct
from core.models.product import ProductVariation
from core.schemas.cart import CartAddProductSchema, CartRemoveProductSchema
from services.mixins.calculate_total_price import CalculateTotalPriceMixin


class CartService(CalculateTotalPriceMixin):
    def __init__(self, session):
        self.session: AsyncSession = session

    async def create_cart(self, user: User) -> Cart:
        cart = Cart(user=user)
        self.session.add(cart)
        await self.session.commit()
        return cart

    async def get_cart(self, user_id: int) -> Cart:
        stmt = select(Cart).where(Cart.user_id == user_id)
        result = await self.session.scalar(stmt)
        return result

    async def add_product_to_cart(self, user: User, data: CartAddProductSchema) -> Cart:
        variation = await self.session.get(ProductVariation, data.variation_id)
        cart = user.cart

        cart_product = await self.session.scalar(
            select(CartProduct)
            .where(CartProduct.cart_id == cart.id)
            .where(CartProduct.product_variation_id == variation.id)
        )

        if cart_product:
            cart_product.quantity += data.quantity
        else:
            cart_product = CartProduct(
                cart_id=cart.id,
                product_variation=variation,
                quantity=data.quantity,
            )
            self.session.add(cart_product)

        await self.session.commit()

        await self.session.refresh(cart)
        cart.total_price = await self.calculate_total_price(cart)
        await self.session.commit()

        return cart

    async def remove_product_from_cart(self, user: User, data: CartRemoveProductSchema) -> Cart:
        cart = user.cart
        cart_product = await self.session.scalar(
            select(CartProduct)
            .where(CartProduct.cart_id == cart.id)
            .where(CartProduct.product_variation_id == data.product_variation_id)
        )
        if cart_product:
            await self.session.delete(cart_product)
            await self.session.commit()

            await self.session.refresh(cart)
            cart.total_price = await self.calculate_total_price(cart)

            await self.session.commit()

        return cart

    async def update_product_quantity(
        self,
        user: User,
        data: CartAddProductSchema,
    ) -> Cart:
        cart = user.cart

        cart_product = await self.session.scalar(
            select(CartProduct)
            .where(CartProduct.cart_id == cart.id)
            .where(CartProduct.product_variation_id == data.variation_id)
        )
        if cart_product:
            cart_product.quantity = data.quantity
            await self.session.commit()

            await self.session.refresh(cart)
            cart.total_price = await self.calculate_total_price(cart)

            await self.session.commit()

        return cart

    async def clear_cart(self, user: User) -> Cart:
        cart = user.cart

        await self.session.execute(delete(CartProduct).where(CartProduct.cart_id == cart.id))

        await self.session.commit()

        await self.session.refresh(cart)
        cart.total_price = await self.calculate_total_price(cart)
        await self.session.commit()

        return cart

    async def cart_is_empty(self, cart: Cart) -> bool:
        return len(cart.products) <= 0
