from datetime import date
from math import ceil

from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission

from app.models.borrow_records import BorrowRecord
from app.models.books import Book
from app.models.members import Member
from app.models.users import User
from app.models.fines import Fine

from app.schemas.borrow_records import (
    BorrowRecordCreate,
    ReturnBookRequest
)

from app.utils.response import api_response


router = APIRouter(
    prefix="/borrow-records",
    tags=["Borrow Records"]
)


#create record

@router.post("")
def borrow_book(
    payload: BorrowRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_borrow_records")
    )
):

    book = db.query(Book).filter(
        Book.id == payload.book_id,
        Book.deleted_at.is_(None)
    ).first()

    if not book:
        return api_response(
            code=404,
            status="Error",
            message="Book not found",
            data=None
        )

    member = db.query(Member).filter(
        Member.id == payload.member_id,
        Member.deleted_at.is_(None)
    ).first()

    if not member:
        return api_response(
            code=404,
            status="Error",
            message="Member not found",
            data=None
        )

    if book.available_copies <= 0:
        return api_response(
            code=400,
            status="Error",
            message="Book is not available",
            data=None
        )

    existing_record = db.query(BorrowRecord).filter(
        BorrowRecord.book_id == payload.book_id,
        BorrowRecord.member_id == payload.member_id,
        BorrowRecord.status == "borrowed",
        BorrowRecord.deleted_at.is_(None)
    ).first()

    if existing_record:
        return api_response(
            code=400,
            status="Error",
            message="Member already borrowed this book",
            data=None
        )

    borrow_record = BorrowRecord(
        book_id=payload.book_id,
        member_id=payload.member_id,
        borrowed_by=current_user.id,
        borrow_date=date.today(),
        due_date=payload.due_date,
        status="borrowed"
    )

    book.available_copies -= 1

    db.add(borrow_record)

    db.commit()
    db.refresh(borrow_record)

    return api_response(
        code=201,
        status="Success",
        message="Book borrowed successfully",
        data={
            "id": borrow_record.id,
            "book_id": borrow_record.book_id,
            "member_id": borrow_record.member_id,
            "borrowed_by": borrow_record.borrowed_by,
            "borrow_date": str(borrow_record.borrow_date),
            "due_date": str(borrow_record.due_date),
            "return_date": borrow_record.return_date,
            "status": borrow_record.status
        }
    )

# custom return date for fine-calculations

from datetime import date
from math import ceil

from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission

from app.models.borrow_records import BorrowRecord
from app.models.books import Book
from app.models.members import Member
from app.models.users import User
from app.models.fines import Fine

from app.schemas.borrow_records import (
    BorrowRecordCreate,
    ReturnBookRequest
)

from app.utils.response import api_response


router = APIRouter(
    prefix="/borrow-records",
    tags=["Borrow Records"]
)


#create record

@router.post("")
def borrow_book(
    payload: BorrowRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_borrow_records")
    )
):

    book = db.query(Book).filter(
        Book.id == payload.book_id,
        Book.deleted_at.is_(None)
    ).first()

    if not book:
        return api_response(
            code=404,
            status="Error",
            message="Book not found",
            data=None
        )

    member = db.query(Member).filter(
        Member.id == payload.member_id,
        Member.deleted_at.is_(None)
    ).first()

    if not member:
        return api_response(
            code=404,
            status="Error",
            message="Member not found",
            data=None
        )

    if book.available_copies <= 0:
        return api_response(
            code=400,
            status="Error",
            message="Book is not available",
            data=None
        )

    existing_record = db.query(BorrowRecord).filter(
        BorrowRecord.book_id == payload.book_id,
        BorrowRecord.member_id == payload.member_id,
        BorrowRecord.status == "borrowed",
        BorrowRecord.deleted_at.is_(None)
    ).first()

    if existing_record:
        return api_response(
            code=400,
            status="Error",
            message="Member already borrowed this book",
            data=None
        )

    borrow_record = BorrowRecord(
        book_id=payload.book_id,
        member_id=payload.member_id,
        borrowed_by=current_user.id,
        borrow_date=date.today(),
        due_date=payload.due_date,
        status="borrowed"
    )

    book.available_copies -= 1

    db.add(borrow_record)

    db.commit()
    db.refresh(borrow_record)

    return api_response(
        code=201,
        status="Success",
        message="Book borrowed successfully",
        data={
            "id": borrow_record.id,
            "book_id": borrow_record.book_id,
            "member_id": borrow_record.member_id,
            "borrowed_by": borrow_record.borrowed_by,
            "borrow_date": str(borrow_record.borrow_date),
            "due_date": str(borrow_record.due_date),
            "return_date": borrow_record.return_date,
            "status": borrow_record.status
        }
    )

# custom return date for fine-calculations

@router.post("/return")
def return_book(
        payload: ReturnBookRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(
            require_permission("manage_borrow_records")
        )
    ):

    record = db.query(BorrowRecord).filter(
        BorrowRecord.id == payload.borrow_record_id,
        BorrowRecord.deleted_at.is_(None)
    ).first()

    if not record:
        return api_response(
            code=404,
            status="Error",
            message="Borrow record not found",
            data=None
        )

    if record.status == "returned":
        return api_response(
            code=400,
            status="Error",
            message="Book already returned",
            data=None
        )

    book = db.query(Book).filter(
        Book.id == record.book_id,
        Book.deleted_at.is_(None)
    ).first()

    if not book:
        return api_response(
            code=404,
            status="Error",
            message="Book not found",
            data=None
        )

    late_days = max(
        0,
        (payload.return_date - record.due_date).days
    )

    if late_days <= 7:
        fine_amount = 0
    else:
        fine_amount = (late_days - 7) * 10

    record.return_date = payload.return_date
    record.late_days = late_days
    record.status = "returned"

    book.available_copies += 1

    existing_fine = db.query(Fine).filter(
        Fine.borrow_record_id == record.id,
        Fine.deleted_at.is_(None)
    ).first()

    if not existing_fine:
        fine = Fine(
            borrow_record_id=record.id,
            member_id=record.member_id,
            late_days=late_days,
            fine_amount=fine_amount,
            status="pending",
            created_by=current_user.id
        )

        db.add(fine)

    db.commit()
    db.refresh(record)

    return api_response(
        code=200,
        status="Success",
        message="Book returned successfully",
        data={
            "id": record.id,
            "book_id": record.book_id,
            "member_id": record.member_id,
            "borrowed_by": record.borrowed_by,
            "borrow_date": str(record.borrow_date),
            "due_date": str(record.due_date),
            "return_date": str(record.return_date),
            "late_days": record.late_days,
            "fine_amount": fine_amount,
            "status": record.status
        }
    )


#get all records

@router.get("")
def get_borrow_records(
    status: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_borrow_records")
    )
):
    query = db.query(BorrowRecord).filter(
        BorrowRecord.deleted_at.is_(None)
    )

    if status:
        query = query.filter(
            BorrowRecord.status == status
        )

    sort_column = getattr(
        BorrowRecord,
        sort_by,
        BorrowRecord.id
    )

    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    total = query.count()

    records = query.offset(
        (page - 1) * limit
    ).limit(limit).all()

    items = []

    for record in records:

        items.append(
            {
                "id": record.id,
                "book_id": record.book_id,
                "member_id": record.member_id,
                "borrowed_by": record.borrowed_by,
                "borrow_date": str(record.borrow_date),
                "due_date": str(record.due_date),
                "return_date": str(record.return_date)
                if record.return_date
                else None,
                "status": record.status
            }
        )

    return api_response(
        code=200,
        status="Success",
        message="Borrow records fetched successfully",
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


# get by id

@router.get("/{record_id}")
def get_borrow_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_borrow_records")
    )
):

    record = db.query(BorrowRecord).filter(
        BorrowRecord.id == record_id,
        BorrowRecord.deleted_at.is_(None)
    ).first()

    if not record:
        return api_response(
            code=404,
            status="Error",
            message="Borrow record not found",
            data=None
        )

    return api_response(
        code=200,
        status="Success",
        message="Borrow record fetched successfully",
        data={
            "id": record.id,
            "book_id": record.book_id,
            "member_id": record.member_id,
            "borrowed_by": record.borrowed_by,
            "borrow_date": str(record.borrow_date),
            "due_date": str(record.due_date),
            "return_date": str(record.return_date)
            if record.return_date
            else None,
            "status": record.status
        }
)

    record = db.query(BorrowRecord).filter(
        BorrowRecord.id == payload.borrow_record_id,
        BorrowRecord.deleted_at.is_(None)
    ).first()

    if not record:
        return api_response(
            code=404,
            status="Error",
            message="Borrow record not found",
            data=None
        )

    if record.status == "returned":
        return api_response(
            code=400,
            status="Error",
            message="Book already returned",
            data=None
        )

    book = db.query(Book).filter(
        Book.id == record.book_id,
        Book.deleted_at.is_(None)
    ).first()

    if not book:
        return api_response(
            code=404,
            status="Error",
            message="Book not found",
            data=None
        )

    late_days = max(
        0,
        (payload.return_date - record.due_date).days
    )

    if late_days <= 7:
        fine_amount = 0
    else:
        fine_amount = (late_days - 7) * 10

    record.return_date = payload.return_date
    record.late_days = late_days
    record.status = "returned"

    book.available_copies += 1

    existing_fine = db.query(Fine).filter(
        Fine.borrow_record_id == record.id,
        Fine.deleted_at.is_(None)
    ).first()

    if not existing_fine:
        fine = Fine(
            borrow_record_id=record.id,
            member_id=record.member_id,
            late_days=late_days,
            fine_amount=fine_amount,
            status="pending",
            created_by=current_user.id
        )

        db.add(fine)

    db.commit()
    db.refresh(record)

    return api_response(
        code=200,
        status="Success",
        message="Book returned successfully",
        data={
            "id": record.id,
            "book_id": record.book_id,
            "member_id": record.member_id,
            "borrowed_by": record.borrowed_by,
            "borrow_date": str(record.borrow_date),
            "due_date": str(record.due_date),
            "return_date": str(record.return_date),
            "late_days": record.late_days,
            "fine_amount": fine_amount,
            "status": record.status
        }
    )


#get all records

@router.get("")
def get_borrow_records(
    status: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_borrow_records")
    )
):
    query = db.query(BorrowRecord).filter(
        BorrowRecord.deleted_at.is_(None)
    )

    if status:
        query = query.filter(
            BorrowRecord.status == status
        )

    sort_column = getattr(
        BorrowRecord,
        sort_by,
        BorrowRecord.id
    )

    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    total = query.count()

    records = query.offset(
        (page - 1) * limit
    ).limit(limit).all()

    items = []

    for record in records:

        items.append(
            {
                "id": record.id,
                "book_id": record.book_id,
                "member_id": record.member_id,
                "borrowed_by": record.borrowed_by,
                "borrow_date": str(record.borrow_date),
                "due_date": str(record.due_date),
                "return_date": str(record.return_date)
                if record.return_date
                else None,
                "status": record.status
            }
        )

    return api_response(
        code=200,
        status="Success",
        message="Borrow records fetched successfully",
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


# get by id

@router.get("/{record_id}")
def get_borrow_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_borrow_records")
    )
):

    record = db.query(BorrowRecord).filter(
        BorrowRecord.id == record_id,
        BorrowRecord.deleted_at.is_(None)
    ).first()

    if not record:
        return api_response(
            code=404,
            status="Error",
            message="Borrow record not found",
            data=None
        )

    return api_response(
        code=200,
        status="Success",
        message="Borrow record fetched successfully",
        data={
            "id": record.id,
            "book_id": record.book_id,
            "member_id": record.member_id,
            "borrowed_by": record.borrowed_by,
            "borrow_date": str(record.borrow_date),
            "due_date": str(record.due_date),
            "return_date": str(record.return_date)
            if record.return_date
            else None,
            "status": record.status
        }
    )