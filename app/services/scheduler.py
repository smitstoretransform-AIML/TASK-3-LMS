from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from app.services.due_reminder import (
    send_due_reminders
)


scheduler = BackgroundScheduler()

scheduler.add_job(
    send_due_reminders,
    "interval",
    hours=24
    # minutes=2
)


def start_scheduler():

    scheduler.start()