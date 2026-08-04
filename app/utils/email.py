import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import BackgroundTasks

from app.core.config import settings


def send_email_task(
    to_email: str,
    subject: str,
    body: str
):

    message = MIMEMultipart()

    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(
        MIMEText(body, "plain")
    )

    server = smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT
    )

    server.starttls()

    server.login(
        settings.SMTP_USERNAME,
        settings.SMTP_PASSWORD
    )

    server.sendmail(
    settings.SMTP_FROM_EMAIL,
    to_email,
    message.as_string()
)

    server.quit()


def send_email(
    background_tasks: BackgroundTasks,
    to_email: str,
    subject: str,
    body: str
):

    background_tasks.add_task(
        send_email_task,
        to_email,
        subject,
        body
    )