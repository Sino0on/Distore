from core.models import Base


class CalculateTotalPriceMixin:
    async def calculate_total_price(self, obj: Base) -> float:
        total_price = 0

        for product in obj.products:
            variation = product.product_variation
            total_price += variation.price * product.quantity

        return total_price
