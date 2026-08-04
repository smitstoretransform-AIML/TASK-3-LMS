from datetime import date
from app.models import BorrowRecord
from math import ceil
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission


from app.models.borrow_records import BorrowRecord
from app.models.members import Member
from app.models.books import Book
from app.models.notifications import Notification
from app.models.users import User

from app.utils.response import api_response

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# due date reminders
@router.post("/generate-due-reminders")
def generate_due_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_notifications")
    )
):

    target_date = date.today() + timedelta(days=2)

    records = db.query(
            BorrowRecord,
            Member,
            Book
        ).join(
            Member,
            BorrowRecord.member_id == Member.id
        ).join(
            Book,
            BorrowRecord.book_id == Book.id
        ).filter(
            BorrowRecord.status == "borrowed",
            BorrowRecord.due_date == target_date
        ).all()

    count = 0

    for record, member, book in records:

        notification = Notification(
            user_id=current_user.id,
            title="Due Reminder",
            message=(
                f"Book '{book.title}' is due in 2 days "
                f"for member '{member.name}' "
                f"(ID: {member.id}). "
                f"Due date: {record.due_date}"
            ),
            type="due_reminder",
            created_by=current_user.id
        )

        db.add(notification)
        count += 1

    db.commit()

    return api_response(
        code=200,
        status="Success",
        message="Due reminders generated successfully",
        data={
            "notifications_created": count
        }
    )

@router.get("")
def get_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_notifications")
    )
):
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.deleted_at.is_(None)
    )   

    total = query.count()

    notifications = query.order_by(
        Notification.created_at.desc()
    ).offset(
        (page - 1) * limit
    ).limit(limit).all()

    items = []

    for notification in notifications:

        items.append(
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "is_read": notification.is_read,
                "created_by": notification.created_by,
                "created_at": notification.created_at
        }
    )

    return api_response(
    code=200,
    status="Success",
    message="Notifications fetched successfully",
    data={
        "items": items,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": ceil(total / limit)
        }
    }
)



@router.get("/{notification_id}")
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_notifications")
    )
):

    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
        Notification.deleted_at.is_(None)
    ).first()

    if not notification:
        return api_response(
            code=404,
            status="Error",
            message="Notification not found",
            data=None
        )

    return api_response(
        code=200,
        status="Success",
        message="Notification fetched successfully",
        data={
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "is_read": notification.is_read,
            "created_by": notification.created_by,
            "created_at": notification.created_at
        }
    )


@router.patch("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_notifications")
    )
):

    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
        Notification.deleted_at.is_(None)
    ).first()

    if not notification:
        return api_response(
            code=404,
            status="Error",
            message="Notification not found",
            data=None
        )

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return api_response(
        code=200,
        status="Success",
        message="Notification marked as read",
        data={
            "id": notification.id,
            "is_read": notification.is_read
        }
    )


@router.patch("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_notifications")
    )
):

    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
        Notification.deleted_at.is_(None)
    ).all()

    count = 0

    for notification in notifications:
        notification.is_read = True
        count += 1

    db.commit()

    return api_response(
        code=200,
        status="Success",
        message="All notifications marked as read",
        data={
            "updated_notifications": count
        }
    )