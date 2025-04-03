from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PaymentSignature(BaseModel):
    signature: str
    params: dict


class PaymentResult(BaseModel):
    pg_order_id: str
    pg_payment_id: int
    pg_amount: str
    pg_currency: str
    pg_net_amount: Optional[str] = None
    pg_ps_amount: Optional[str] = None
    pg_ps_full_amount: Optional[str] = None
    pg_ps_currency: Optional[str] = None
    pg_description: str
    pg_result: int
    pg_payment_date: datetime
    pg_can_reject: int
    pg_user_phone: Optional[str] = None
    pg_user_contact_email: Optional[str] = None
    pg_need_email_notification: Optional[int] = None
    pg_testing_mode: Optional[int] = None
    pg_captured: Optional[int] = None
    pg_card_pan: Optional[str] = None
    pg_salt: str
    pg_sig: str
    pg_payment_method: Optional[str] = None
    pg_delivery: Optional[bool] = None

    model_config = ConfigDict(extra="allow")


class PaymentRequestParams(BaseModel):
    pg_order_id: int
    pg_amount: float | int
    pg_currency: str
    pg_description: str
    pg_salt: str = 'distore'
    pg_sig: str

    model_config = ConfigDict(extra="allow")


class PaymentUrlResponse(BaseModel):
    redirect_url: str