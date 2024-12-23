from pydantic import BaseModel, EmailStr


class HelpForm(BaseModel):
    phone: str
    email: EmailStr