from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from app.models.borrow_records import BorrowRecord
from app.models.books import Book
from app.models.members import Member

from app.utils.notification_service import (
    create_notification_with_email
)


def send_due_reminders():

    db: Session = SessionLocal()

    try:

        target_date = date.today() + timedelta(days=2)

        records = db.query(
            BorrowRecord
        ).filter(
            BorrowRecord.due_date == target_date,
            BorrowRecord.status == "borrowed"
        ).all()

        for record in records:

            member = db.query(Member).filter(
                Member.id == record.member_id
            ).first()

            book = db.query(Book).filter(
                Book.id == record.book_id
            ).first()

            create_notification_with_email(
                db=db,
                background_tasks=None,
                user_id=record.borrowed_by,
                email=member.email,
                title="Book Due Reminder",
                message=(
                    f"Hello {member.name},\n\n"
                    f"Your book '{book.title}' "
                    f"(ID: {book.id}) is due on "
                    f"{record.due_date}.\n"
                    f"Please return it on time."
                ),
                notification_type="due_reminder",
                created_by=record.borrowed_by
            )

        db.commit()

    finally:
        db.close()