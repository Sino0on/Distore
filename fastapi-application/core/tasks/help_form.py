from celery import shared_task

from core.config import settings
from utils.email_sender import send_email


@shared_task(bind=True, name="send_help_form_email")
def send_help_form_email(self, body_data: dict) -> None:
    print(f"Send help form email: {body_data}")

    send_email(
        "Заявка на консультацию",
        settings.admin_email,
        body_data,
        "email/help_form.html",
    )
