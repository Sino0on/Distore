from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import HTTPBearer

from core.config import settings

from .auth import router as auth_router
from .users import router as users_router
from .brands import router as brands_router
from .categories import router as categories_router
from .products import router as products_router
from .carts import router as carts_router
from .orders import router as orders_router
from .messages import router as messages_router
from .uds import router as uds_router
from .help_form import router as help_form_router
from .banners import router as banner_router
from .payments import router as payments_router
from .properties import router as properties_router
from .delivery import router as delivery_router


http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix=settings.api.v1.prefix,
    dependencies=[Depends(http_bearer)],
)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(brands_router)
router.include_router(categories_router)
router.include_router(properties_router)
router.include_router(delivery_router)
router.include_router(products_router)
router.include_router(carts_router)
router.include_router(orders_router)
router.include_router(uds_router)
router.include_router(payments_router)
router.include_router(help_form_router)
router.include_router(banner_router)
# router.include_router(messages_router)
