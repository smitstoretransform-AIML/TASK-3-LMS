from datetime import date

from pydantic import BaseModel, field_validator


class BorrowRecordCreate(BaseModel):

    book_id: int
    member_id: int
    due_date: date

    @field_validator("book_id")
    @classmethod
    def validate_book_id(cls, value):

        if value <= 0:
            raise ValueError(
                "Book ID must be greater than 0"
            )

        return value

    @field_validator("member_id")
    @classmethod
    def validate_member_id(cls, value):

        if value <= 0:
            raise ValueError(
                "Member ID must be greater than 0"
            )

        return value

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value):

        if value <= date.today():
            raise ValueError(
                "Due date must be greater than today"
            )

        return value


class ReturnBookSchema(BaseModel):
    pass


class BorrowRecordResponse(BaseModel):

    id: int
    book_id: int
    member_id: int
    borrowed_by: int

    borrow_date: date
    due_date: date
    return_date: date | None

    status: str

    class Config:
        from_attributes = True


# RETURN BOOK SCHEMA

class ReturnBookRequest(BaseModel):

    borrow_record_id: int
    return_date: date

    @field_validator("borrow_record_id")
    @classmethod
    def validate_borrow_record_id(cls, value):

        if value <= 0:
            raise ValueError(
                "Borrow record ID must be greater than 0"
            )

        return value