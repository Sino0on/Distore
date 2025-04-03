from pathlib import Path

from fastapi_mail import ConnectionConfig
from fastapi_storages import FileSystemStorage
from pydantic import BaseModel, RedisDsn
from pydantic import PostgresDsn
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    users: str = "/users"
    messages: str = "/messages"
    brands: str = "/brands"
    categories: str = "/categories"
    products: str = "/products"
    carts: str = "/carts"
    orders: str = "/orders"
    payments: str = "/payments"
    uds: str = "/uds"
    help_form: str = "/help-form"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()

    @property
    def bearer_token_url(self) -> str:
        # api/v1/auth/login
        parts = (self.prefix, self.v1.prefix, self.v1.auth, "/login")
        path = "".join(parts)
        # return path[1:]
        return path.removeprefix("/")


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class RedisConfig(BaseModel):
    url: str


class AccessToken(BaseModel):
    lifetime_seconds: int = 24 * 60 * 60
    reset_password_token_secret: str
    verification_token_secret: str


class EmailConfig(BaseModel):
    mail_server: str
    mail_port: int
    mail_username: str
    mail_password: str
    mail_from: str
    mail_from_name: str = "Distore"
    mail_tls: bool = True
    mail_ssl: bool = False
    mail_use_credentials: bool = True
    mail_template_folder: str = Path(__file__).parent / "templates"


class FrontendConfig(BaseModel):
    reset_password_url: str


class UDSConfig(BaseModel):
    username: str
    password: str
    origin_request_id: str
    uds_customer_find_url: str = "https://api.uds.app/partner/v2/customers/find"
    uds_transaction_calc_url: str = "https://api.uds.app/partner/v2/operations/calc"
    uds_transaction_create_url: str = "https://api.uds.app/partner/v2/operations"
    uds_transaction_refund_url: str = "https://api.uds.app/partner/v2/operations/{transaction_id}/refund"


class Config1C(BaseModel):
    username: str
    password: str
    brands_url: str
    categories_url: str
    products_url: str
    order_create_url: str


class FreedomPayConfig(BaseModel):
    merchant_id: int
    secret_key: str
    init_payment_url: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="ignore",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig
    redis: RedisConfig
    access_token: AccessToken
    email_config: EmailConfig
    frontend_config: FrontendConfig
    uds_config: UDSConfig
    config_1c: Config1C
    freedom_pay_config: FreedomPayConfig

    domain: str
    page_size_default: int = 20
    admin_email: str
    static_files_path: Path = Path(__file__).parent.parent / "static"

    @property
    def file_storage(self):
        storage = FileSystemStorage(path=str(self.static_files_path.resolve()))

        return storage


    @property
    def mail_connection_config(self) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_SERVER=self.email_config.mail_server,
            MAIL_PORT=self.email_config.mail_port,
            MAIL_USERNAME=self.email_config.mail_username,
            MAIL_PASSWORD=self.email_config.mail_password,
            MAIL_FROM=self.email_config.mail_from,
            MAIL_FROM_NAME=self.email_config.mail_from_name,
            MAIL_STARTTLS=self.email_config.mail_tls,
            MAIL_SSL_TLS=self.email_config.mail_ssl,
            USE_CREDENTIALS=self.email_config.mail_use_credentials,
            TEMPLATE_FOLDER=self.email_config.mail_template_folder,
        )


settings = Settings()
