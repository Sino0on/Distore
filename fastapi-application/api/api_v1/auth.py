from fastapi import APIRouter, status, Request, Depends, HTTPException
from fastapi_users import BaseUserManager, exceptions
from fastapi_users.router.common import ErrorModel, ErrorCode

from api.api_v1.fastapi_users import fastapi_users
from api.dependencies.authentication import authentication_backend, get_user_manager, \
    get_database_strategy
from core.config import settings
from core.schemas.user import (
    UserRead,
    UserCreate,
)

router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)

# /login
# /logout
router.include_router(
    router=fastapi_users.get_auth_router(
        authentication_backend,
        # requires_verification=True,
    ),
)


# /register

# router.include_router(
#     router=fastapi_users.get_register_router(
#         UserRead,
#         UserCreate,
#     ),
# )

@router.post(
    "/register",
        status_code=status.HTTP_201_CREATED,
        name="register:register",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {
                                    "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                                },
                            },
                            ErrorCode.REGISTER_INVALID_PASSWORD: {
                                "summary": "Password validation failed.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                        "reason": "Password should be"
                                        "at least 3 characters",
                                    }
                                },
                            },
                        }
                    }
                },
            },
        },)
async def custom_register(
        request: Request,
        user_create: UserCreate,  # type: ignore
        user_manager: BaseUserManager = Depends(get_user_manager),
        strategy=Depends(get_database_strategy),
):
    try:
        created_user = await user_manager.create(
            user_create, safe=True, request=request
        )
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
    except:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.REGISTER_USER_ALREADY_EXISTS,
                "reason": 'Username has taken',
            },
        )

    response = await authentication_backend.login(strategy, created_user)
    await user_manager.on_after_login(created_user, request, response)

    return response

# /request-verify-token
# /verify
# router.include_router(
#     router=fastapi_users.get_verify_router(UserRead),
# )

# /forgot-password
# /reset-password
router.include_router(
    router=fastapi_users.get_reset_password_router(),
)
