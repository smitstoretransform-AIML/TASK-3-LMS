from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text
)
from sqlalchemy.sql import func

from app.core.database import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False
    )

    phone = Column(
        String(20),
        nullable=False
    )

    address = Column(
        Text,
        nullable=False
    )

    membership_date = Column(
        Date,
        nullable=False
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