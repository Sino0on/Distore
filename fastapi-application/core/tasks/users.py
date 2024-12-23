from celery import shared_task

from utils.email_sender import send_email


@shared_task(bind=True, name="send_forget_password_email")
def send_forget_password_email(
    self, subject: str, email_to: str, body_data: dict, template_name: str
) -> None:
    print(f"Send forget password email to {email_to}")

    send_email(subject, email_to, body_data, template_name)
