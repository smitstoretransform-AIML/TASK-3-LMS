from app.utils import email
from fastapi import BackgroundTasks

from app.models.notifications import Notification
from app.utils.email import send_email_task

def create_notification_with_email(
    db,
    background_tasks: BackgroundTasks,
    user_id: int,
    email: str,
    title: str,
    message: str,
    notification_type: str,
    created_by: int
):
    print("Notification helper called")

    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type,
        created_by=created_by
    )

    db.add(notification)

    if background_tasks:

        background_tasks.add_task(
            send_email_task,
            email,
            title,
            message
        )

    else:

        send_email_task(
            email,
            title,
            message 
    )