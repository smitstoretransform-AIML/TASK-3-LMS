from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    String
)
from sqlalchemy.sql import func

from app.core.database import Base


class Fine(Base):
    __tablename__ = "fines"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    borrow_record_id = Column(
        BigInteger,
        ForeignKey("borrow_records.id"),
        nullable=False
    )

    member_id = Column(
        BigInteger,
        ForeignKey("members.id"),
        nullable=False
    )

    late_days = Column(
        BigInteger,
        nullable=False,
        server_default="0"
    )

    fine_amount = Column(
        BigInteger,
        nullable=False,
        server_default="0"
    )

    status = Column(
        String(20),
        nullable=False,
        server_default="pending"
    )

    paid_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_by = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
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