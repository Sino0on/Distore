from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import Category, db_helper
from core.schemas.helpl_form import HelpForm
from core.tasks.help_form import send_help_form_email
from utils.email_sender import send_email

router = APIRouter(
    prefix=settings.api.v1.help_form,
    tags=["Help"],
)


@router.post("", status_code=200)
async def receive_help_form(form: HelpForm):
    send_help_form_email.apply_async(kwargs={"body_data": form.model_dump()})
