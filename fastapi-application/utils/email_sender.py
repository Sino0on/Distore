import smtplib
from email.message import EmailMessage

from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema, FastMail, ConnectionConfig, MessageType
from jinja2 import Environment, FileSystemLoader

from core.config import settings


def send_email_background(
    background_tasks: BackgroundTasks, subject: str, email_to: str, body: dict, template_name: str
):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
        subtype=MessageType.html,
    )
    fm = FastMail(settings.mail_connection_config)
    background_tasks.add_task(fm.send_message, message, template_name=template_name)


async def send_email_async(subject: str, email_to: str, body: dict, template_name: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
        subtype=MessageType.html,
    )

    fm = FastMail(settings.mail_connection_config)
    await fm.send_message(message, template_name=template_name)


def send_email(subject: str, email_to: str, body_data: dict, template_name: str):
    environment = Environment(loader=FileSystemLoader(settings.email_config.mail_template_folder))
    template = environment.get_template(template_name)
    body = template.render(body_data)

    message = EmailMessage()
    message["From"] = settings.email_config.mail_from
    message["To"] = email_to
    message["Subject"] = subject
    message.set_content(body, subtype="html")

    with smtplib.SMTP_SSL(
        settings.email_config.mail_server,
        settings.email_config.mail_port,
    ) as smtp:
        smtp.login(settings.email_config.mail_username, settings.email_config.mail_password)
        smtp.send_message(message)