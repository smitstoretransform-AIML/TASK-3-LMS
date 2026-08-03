from datetime import datetime, timezone
from math import ceil

from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    require_permission
)
from app.models.books import Book
from app.models.users import User
from app.schemas.books import BookCreate, BookUpdate
from app.utils.response import api_response


router = APIRouter(
    prefix="/books",
    tags=["Books"]
)


# CREATE BOOK


@router.post("")
def create_book(
    payload: BookCreate,
    db: Session = Depends(get_db),
   current_user: User = Depends(
    require_permission("create_book")
)
):

   
    existing_book = db.query(Book).filter(
        Book.isbn == payload.isbn,
        Book.deleted_at.is_(None)
    ).first()

    if existing_book:
        return api_response(
            code=400,
            status="Error",
            message="ISBN already exists",
            data=None
        )

    book = Book(
        title=payload.title,
        author=payload.author,
        isbn=payload.isbn,
        category=payload.category,
        publisher=payload.publisher,
        total_copies=payload.total_copies,
        available_copies=payload.total_copies,
        created_by=current_user.id
    )

    db.add(book)
    db.commit()
    db.refresh(book)

    return api_response(
        code=201,
        status="Success",
        message="Book created successfully",
        data={
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "category": book.category,
            "publisher": book.publisher,
            "total_copies": book.total_copies,
            "available_copies": book.available_copies
        }
    )


# GET ALL BOOKS


@router.get("")
def get_books(
    search: str = None,
    category: str = None,
    author: str = None,
    available: bool = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
   current_user: User = Depends(
    require_permission("view_books")
)
):

    if not current_user:
        return api_response(
            code=401,
            status="Error",
            message="Unauthorized",
            data=None
        )

    query = db.query(Book).filter(
        Book.deleted_at.is_(None)
    )

    if search:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%"),
                Book.isbn.ilike(f"%{search}%")
            )
        )

    if category:
        query = query.filter(
            Book.category.ilike(f"%{category}%")
        )

    if author:
        query = query.filter(
            Book.author.ilike(f"%{author}%")
        )

    if available is True:
        query = query.filter(
            Book.available_copies > 0
        )

    sort_column = getattr(Book, sort_by, Book.id)

    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    total = query.count()

    books = query.offset(
        (page - 1) * limit
    ).limit(limit).all()

    items = []

    for book in books:
        items.append(
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "category": book.category,
                "publisher": book.publisher,
                "total_copies": book.total_copies,
                "available_copies": book.available_copies
            }
        )

    return api_response(
        code=200,
        status="Success",
        message="Books fetched successfully",
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


# GET BOOK BY ID


@router.get("/{book_id}")
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
   current_user: User = Depends(
    require_permission("view_books")
)
):

    book = db.query(Book).filter(
        Book.id == book_id,
        Book.deleted_at.is_(None)
    ).first()

    if not book:
        return api_response(
            code=404,
            status="Error",
            message="Book not found",
            data=None
        )

    return api_response(
        code=200,
        status="Success",
        message="Book fetched successfully",
        data={
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "category": book.category,
            "publisher": book.publisher,
            "total_copies": book.total_copies,
            "available_copies": book.available_copies
        }
    )


# UPDATE BOOK


@router.put("/{book_id}")
def update_book(
    book_id: int,
    payload: BookUpdate,
    db: Session = Depends(get_db),
   current_user: User = Depends(
    require_permission("update_book")
)
):

    book = db.query(Book).filter(
        Book.id == book_id,
        Book.deleted_at.is_(None)
    ).first()

    if not book:
        return api_response(
            code=404,
            status="Error",
            message="Book not found",
            data=None
        )

        borrowed_count = (
        book.total_copies - book.available_copies
    )

    # CHECK ISBN UNIQUENESS

    if payload.isbn:

        existing_isbn = db.query(Book).filter(
            Book.isbn == payload.isbn,
            Book.id != book_id,
            Book.deleted_at.is_(None)
        ).first()

        if existing_isbn:
            return api_response(
                code=400,
                status="Error",
                message="ISBN already exists",
                data=None
            )

        update_data = payload.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(book, key, value)
    if payload.total_copies is not None:

        if payload.total_copies < borrowed_count:
            return api_response(
                code=400,
                status="Error",
                message="Total copies cannot be less than borrowed books",
                data=None
            )

        book.available_copies = (
            payload.total_copies - borrowed_count
        )

    book.updated_by = current_user.id

    db.commit()
    db.refresh(book)

    return api_response(
        code=200,
        status="Success",
        message="Book updated successfully",
        data={
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "category": book.category,
            "publisher": book.publisher,
            "total_copies": book.total_copies,
            "available_copies": book.available_copies
        }
    )


# DELETE BOOK


@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
   current_user: User = Depends(
    require_permission("delete_book")
)
):

    book = db.query(Book).filter(
        Book.id == book_id,
        Book.deleted_at.is_(None)
    ).first()

    if not book:
        return api_response(
            code=404,
            status="Error",
            message="Book not found",
            data=None
        )

    borrowed_count = (
        book.total_copies - book.available_copies
    )

    if borrowed_count > 0:
        return api_response(
            code=400,
            status="Error",
            message="Book cannot be deleted because it is currently borrowed",
            data=None
        )

    book.deleted_at = datetime.now(
        timezone.utc
    )

    db.commit()

    return api_response(
        code=200,
        status="Success",
        message="Book deleted successfully",
        data=None
    )