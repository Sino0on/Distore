from typing import Optional

from pydantic import BaseModel


class UDSDataRead(BaseModel):
    uid: str
    points: int | float


class UDSTransactionData(BaseModel):
    id: int
    date_created: Optional[str] = None
    action: str
    state: str
    points: int | float
    cash: int
    total: int
