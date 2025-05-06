from contextlib import asynccontextmanager
from fastapi import Request
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
# from sqladmin import Admin
from fastapi.middleware.cors import CORSMiddleware

from core.admin import create_admin
from core.config import settings
from core.celery import app as celery_app

from api import router as api_router
from core.models import db_helper
from core.models.db_helper import AsyncSessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await db_helper.dispose()


main_app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

@main_app.middleware("http")
async def add_session_to_state(request: Request, call_next):
    async with AsyncSessionLocal() as session:
        request.state.session = session
        response = await call_next(request)
    return response

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Headers",
        "Set-Cookie",
        "Token",
    ],
)

main_app.include_router(
    api_router,
)

admin = create_admin(main_app)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
        forwarded_allow_ips="*",
        proxy_headers=True,
    )
