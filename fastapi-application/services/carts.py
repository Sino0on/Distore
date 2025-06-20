from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from core.models import Cart, User, Group, Category, Product
from core.models.cart import CartProduct
from core.models.product import ProductVariation
from core.schemas.cart import CartAddProductSchema, CartRemoveProductSchema
from services.mixins.calculate_total_price import CalculateTotalPriceMixin


class CartService(CalculateTotalPriceMixin):
    ATOMIZER_PRODUCT_ID = 31380
    ATOMIZER_VOLUME_MAP = {
        "5 мл": 5,
        "10 мл": 10,
        "15 мл": 15,
    }
    PERFUME_GROUP_NAME = "Парфюм"
    PERFUME_VOLUME_PROPERTY_NAME = "Объем"
    PERFUME_BASE_VOLUME_VALUES = ("1 мл", "1мл", "1ml", "1 ml")

    def __init__(self, session):
        self.session: AsyncSession = session
        self._atomizer_variations: list[ProductVariation] | None = None
        self._atomizer_variation_map: dict[int, ProductVariation] | None = None

    async def _get_atomizer_variation_map(self) -> dict[int, ProductVariation]:
        """Кэширует и возвращает карту 'объем -> вариация' для атомайзеров."""
        if self._atomizer_variation_map is None:
            stmt = select(ProductVariation).where(
                ProductVariation.product_id == self.ATOMIZER_PRODUCT_ID
                )
            variations = (await self.session.execute(stmt)).scalars().all()
            self._atomizer_variation_map = {
                self.ATOMIZER_VOLUME_MAP[var.name]: var
                for var in variations if var.name in self.ATOMIZER_VOLUME_MAP
            }
        return self._atomizer_variation_map

    def _is_perfume_1ml(self, variation: ProductVariation) -> bool:
        """Проверяет, является ли вариация 'Парфюмом' с объемом '1 мл'."""
        if not variation.product:
            return False

        is_perfume_group = (
            variation.product.category
            and variation.product.category.group
            and variation.product.category.group.name == self.PERFUME_GROUP_NAME
        )
        if not is_perfume_group:
            return False

        for prop in variation.properties:
            if (
                prop.name == self.PERFUME_VOLUME_PROPERTY_NAME
                and prop.value in self.PERFUME_BASE_VOLUME_VALUES
            ):
                return True

        return False

    async def _sync_atomizers_for_product(
            self,
            perfume_cart_product: CartProduct,
            is_new: bool,
    ):
        """
        Эффективно синхронизирует атомайзеры для ОДНОГО парфюма.
        Сравнивает текущее состояние с целевым и применяет только разницу.
        """
        target_state: dict[int, int] = {}  # {variation_id: quantity}
        needed_volume = perfume_cart_product.quantity

        if needed_volume > 0:
            atomizer_map = await self._get_atomizer_variation_map()
            if atomizer_map:
                remaining_volume = needed_volume
                sorted_volumes_desc = sorted(atomizer_map.keys(), reverse=True)

                for vol_size in sorted_volumes_desc:
                    if remaining_volume < 15:
                        break

                    if remaining_volume >= vol_size:
                        count = remaining_volume // vol_size
                        variation = atomizer_map[vol_size]
                        target_state[variation.id] = target_state.get(
                            variation.id, 0
                            ) + count
                        remaining_volume %= vol_size

                if remaining_volume > 0:
                    sorted_volumes_asc = sorted(atomizer_map.keys())
                    best_fit_volume = None

                    for vol_size in sorted_volumes_asc:
                        if vol_size >= remaining_volume:
                            best_fit_volume = vol_size
                            break

                    if best_fit_volume:
                        variation = atomizer_map[best_fit_volume]
                        target_state[variation.id] = target_state.get(
                            variation.id, 0
                            ) + 1
                    else:
                        if sorted_volumes_desc:
                            largest_volume = sorted_volumes_desc[0]
                            variation = atomizer_map[largest_volume]
                            target_state[variation.id] = target_state.get(
                                variation.id, 0
                                ) + 1

        if is_new:
            current_state: dict[int, CartProduct] = {}
        else:
            current_state: dict[int, CartProduct] = {
                child.product_variation_id: child for child in
                perfume_cart_product.children
            }

        for target_var_id, target_quantity in target_state.items():
            if target_var_id in current_state:
                # Атомайзер уже есть, проверяем количество
                cart_product_to_update = current_state[target_var_id]
                if cart_product_to_update.quantity != target_quantity:
                    cart_product_to_update.quantity = target_quantity

                del current_state[target_var_id]
            else:
                # Атомайзера нет, добавляем
                self.session.add(
                    CartProduct(
                        cart_id=perfume_cart_product.cart_id,
                        product_variation_id=target_var_id,
                        quantity=target_quantity,
                        parent_cart_product_id=perfume_cart_product.id,
                    )
                )

        # Все, что осталось в `current_state`, - лишнее и подлежит удалению
        for cart_product_to_delete in current_state.values():
            await self.session.delete(cart_product_to_delete)

    async def _process_cart_update(self, cart: Cart):
        """Общая функция для коммита, обновления и пересчета цены."""
        await self.session.commit()
        await self.session.refresh(cart)
        cart.total_price = await self.calculate_total_price(cart)
        await self.session.commit()
        await self.session.refresh(cart)

    async def create_cart(self, user: User) -> Cart:
        cart = Cart(user=user)
        self.session.add(cart)
        await self.session.commit()
        return cart

    async def get_cart(self, user_id: int) -> Cart:
        stmt = select(Cart).where(Cart.user_id == user_id)
        result = await self.session.scalar(stmt)
        return result

    async def add_product_to_cart(
            self,
            user: User,
            data: CartAddProductSchema,
    ) -> Cart:
        variation = await self.session.get(
            ProductVariation,
            data.variation_id,
            options=[
                joinedload(ProductVariation.product)
                .joinedload(Product.category)
                .joinedload(Category.group),
                selectinload(ProductVariation.properties)
            ]
        )
        cart = user.cart

        cart_product = await self.session.scalar(
            select(CartProduct).where(
                CartProduct.cart_id == cart.id,
                CartProduct.product_variation_id == variation.id
                )
            .options(
                selectinload(CartProduct.children)
            )
        )

        is_new_product = False

        if cart_product:
            cart_product.quantity += data.quantity
        else:
            cart_product = CartProduct(
                cart_id=cart.id, product_variation=variation,
                quantity=data.quantity
            )
            self.session.add(cart_product)
            is_new_product = True

        await self.session.flush()

        if self._is_perfume_1ml(variation):
            await self._sync_atomizers_for_product(
                cart_product,
                is_new=is_new_product,
            )

        await self._process_cart_update(cart)
        return cart

    async def update_product_quantity(
            self,
            user: User,
            data: CartAddProductSchema,
    ) -> Cart:
        cart = user.cart
        cart_product = await self.session.scalar(
            select(CartProduct).where(
                CartProduct.cart_id == cart.id,
                CartProduct.product_variation_id == data.variation_id
                )
            .options(
                selectinload(CartProduct.children),
                joinedload(CartProduct.product_variation)
                .selectinload(ProductVariation.properties),
                joinedload(CartProduct.product_variation)
                .joinedload(ProductVariation.product)
                .joinedload(Product.category)
                .joinedload(Category.group),
                )
        )
        if not cart_product:
            return cart

        if data.quantity <= 0:
            await self.session.delete(cart_product)
        else:
            cart_product.quantity = data.quantity
            await self.session.flush()
            if self._is_perfume_1ml(cart_product.product_variation):
                await self._sync_atomizers_for_product(
                    cart_product,
                    is_new=False,
                )

        await self._process_cart_update(cart)
        return cart

    async def remove_product_from_cart(
            self,
            user: User,
            data: CartRemoveProductSchema,
    ) -> Cart:
        cart = user.cart
        cart_product = await self.session.scalar(
            select(CartProduct).where(
                CartProduct.cart_id == cart.id,
                CartProduct.product_variation_id == data.product_variation_id
                )
        )
        if cart_product:
            await self.session.delete(cart_product)
            await self._process_cart_update(cart)

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
