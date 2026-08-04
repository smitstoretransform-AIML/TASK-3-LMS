from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission

from app.models.books import Book
from app.models.members import Member
from app.models.borrow_records import BorrowRecord
from app.models.fines import Fine
from app.models.users import User

from app.utils.response import api_response

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("")
def get_dashboard(

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_permission("view_dashboard")
    )
    ):

    total_books = db.query(Book).filter(
        Book.deleted_at.is_(None)
    ).count()

    total_members = db.query(Member).filter(
        Member.deleted_at.is_(None)
    ).count()

    borrowed_books = db.query(BorrowRecord).filter(
        BorrowRecord.status == "borrowed",
        BorrowRecord.deleted_at.is_(None)
    ).count()

    available_books = db.query(
        func.sum(Book.available_copies)
    ).scalar() or 0

    pending_fines = db.query(Fine).filter(
        Fine.status == "pending",
        Fine.deleted_at.is_(None)
    ).count()

    total_fine_amount = db.query(
        func.sum(Fine.fine_amount)
    ).filter(
        Fine.status == "pending",
        Fine.deleted_at.is_(None)
    ).scalar() or 0

    return api_response(
    code=200,
    status="Success",
    message="Dashboard data fetched successfully",
    data={
        "total_books": total_books,
        "total_members": total_members,
        "borrowed_books": borrowed_books,
        "available_books": available_books,
        "pending_fines": pending_fines,
        "total_fine_amount": total_fine_amount
    }
)