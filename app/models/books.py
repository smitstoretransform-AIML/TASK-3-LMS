from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String
)
from sqlalchemy.sql import func

from app.core.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    author = Column(
        String(255),
        nullable=False
    )

    isbn = Column(
        String(20),
        unique=True,
        nullable=False
    )

    category = Column(
        String(100),
        nullable=False
    )

    publisher = Column(
        String(255),
        nullable=True
    )

    total_copies = Column(
        Integer,
        nullable=False,
        default=0
    )

    available_copies = Column(
        Integer,
        nullable=False,
        default=0
    )

    created_by = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    updated_by = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True
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