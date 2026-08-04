from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission

from app.models.books import Book
from app.models.borrow_records import BorrowRecord
from app.models.members import Member
from app.models.users import User

from app.utils.response import api_response

from math import ceil


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/borrow-history")
def borrow_history(
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_reports")
    )
):

    query = db.query(
        BorrowRecord,
        Book,
        Member
    ).join(
        Book,
        BorrowRecord.book_id == Book.id
    ).join(
        Member,
        BorrowRecord.member_id == Member.id
    ).filter(
        BorrowRecord.deleted_at.is_(None)
    )

    if start_date:
        query = query.filter(
            BorrowRecord.borrow_date >= start_date
        )

    if end_date:
        query = query.filter(
            BorrowRecord.borrow_date <= end_date
        )

    total = query.count()

    results = query.offset(
        (page - 1) * limit
    ).limit(limit).all()

    items = []

    for record, book, member in results:

        items.append(
            {
                "borrow_record_id": record.id,
                "book_title": book.title,
                "member_name": member.name,
                "borrow_date": record.borrow_date,
                "due_date": record.due_date,
                "return_date": record.return_date,
                "status": record.status
            }
        )

    return api_response(
        code=200,
        status="Success",
        message="Borrow history fetched successfully",
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


@router.get("/member-history/{member_id}")
def member_history(
    member_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_reports")
    )
):

    member = db.query(Member).filter(
        Member.id == member_id,
        Member.deleted_at.is_(None)
    ).first()

    if not member:
        return api_response(
            code=404,
            status="Error",
            message="Member not found",
            data=None
        )

    query = db.query(
        BorrowRecord,
        Book
    ).join(
        Book,
        BorrowRecord.book_id == Book.id
    ).filter(
        BorrowRecord.member_id == member_id,
        BorrowRecord.deleted_at.is_(None)
    )

    total = query.count()

    results = query.offset(
        (page - 1) * limit
    ).limit(limit).all()

    items = []

    for record, book in results:

        items.append(
            {
                "borrow_record_id": record.id,
                "book_id": book.id,
                "book_title": book.title,
                "borrow_date": record.borrow_date,
                "due_date": record.due_date,
                "return_date": record.return_date,
                "status": record.status,
            }
        )

    return api_response(
        code=200,
        status="Success",
        message="Member history fetched successfully",
        data={
            "member": {
                "id": member.id,
                "name": member.name
            },
            "items": items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": ceil(total / limit)
            }
        }
    )



from datetime import date


@router.get("/overdue-books")
def overdue_books(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_reports")
    )
):

    query = db.query(
        BorrowRecord,
        Book,
        Member
    ).join(
        Book,
        BorrowRecord.book_id == Book.id
    ).join(
        Member,
        BorrowRecord.member_id == Member.id
    ).filter(
        BorrowRecord.status == "borrowed",
        BorrowRecord.due_date < date.today(),
        BorrowRecord.deleted_at.is_(None)
    )

    total = query.count()

    results = query.offset(
        (page - 1) * limit
    ).limit(limit).all()

    items = []

    for record, book, member in results:

        late_days = (
            date.today() - record.due_date
        ).days

        items.append(
            {
                "borrow_record_id": record.id,
                "book_title": book.title,
                "member_name": member.name,
                "borrow_date": record.borrow_date,
                "due_date": record.due_date,
                "late_days": late_days,
            }
        )

    return api_response(
        code=200,
        status="Success",
        message="Overdue books fetched successfully",
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



from sqlalchemy import func, desc


@router.get("/most-borrowed-books")
def most_borrowed_books(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_reports")
    )
):

    query = db.query(
        Book.id,
        Book.title,
        func.count(
            BorrowRecord.id
        ).label(
            "borrow_count"
        )
    ).join(
        BorrowRecord,
        BorrowRecord.book_id == Book.id
    ).group_by(
        Book.id,
        Book.title
    ).order_by(
        desc("borrow_count")
    )

    total = query.count()

    results = query.offset(
        (page - 1) * limit
    ).limit(limit).all()

    items = []

    for book_id, title, borrow_count in results:

        items.append(
            {
                "book_id": book_id,
                "book_title": title,
                "borrow_count": borrow_count
            }
        )

    return api_response(
        code=200,
        status="Success",
        message="Most borrowed books fetched successfully",
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
