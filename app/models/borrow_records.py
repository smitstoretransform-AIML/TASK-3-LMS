from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    ForeignKey,
    String
)
from sqlalchemy.sql import func

from app.core.database import Base


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    book_id = Column(
        BigInteger,
        ForeignKey("books.id"),
        nullable=False
    )

    member_id = Column(
        BigInteger,
        ForeignKey("members.id"),
        nullable=False
    )

    borrowed_by = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    borrow_date = Column(
        Date,
        nullable=False
    )

    due_date = Column(
        Date,
        nullable=False
    )

    return_date = Column(
        Date,
        nullable=True
    )

    late_days = Column(
        BigInteger,
        nullable=False,
        server_default="0"
    )

    status = Column(
        String(20),
        nullable=False,
        server_default="borrowed"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )