from typing import Optional, TYPE_CHECKING

from fastapi import Depends
from fastapi_users import (
    BaseUserManager,
    IntegerIDMixin,
)
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import User, db_helper, Cart
from core.tasks.users import send_forget_password_email
from core.types.user_id import UserIdType
from services.carts import CartService

if TYPE_CHECKING:
    from fastapi import Request


class UserManager(IntegerIDMixin, BaseUserManager[User, UserIdType]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    async def on_after_register(
        self,
        user: User,
        request: Optional["Request"] = None,
    ):
        logger.warning(
            "User %r has registered.",
            user.id,
        )
        async with db_helper.session_factory() as session:
            user = await session.merge(user)
            cart_service = CartService(session)
            await cart_service.create_cart(user)

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ):
        logger.warning(
            "Verification requested for user %r. Verification token: %r",
            user.id,
            token,
        )

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ):
        logger.warning(
            f"User {user.id} has forgot their password. Reset token: {token}"
        )

        send_forget_password_email.apply_async(
            kwargs={
                "subject": "Reset your password",
                "email_to": user.email,
                "body_data": {
                    "name": user.nickname,
                    "url": f"{settings.frontend_config.reset_password_url}/{token}",
                },
                "template_name": "email/forgot_password.html",
            }
        )
