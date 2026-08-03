from datetime import datetime
from pydantic import BaseModel


class FineResponse(BaseModel):

    id: int
    borrow_record_id: int
    member_id: int
    late_days: int
    fine_amount: int
    status: str
    paid_at: datetime | None = None
    created_by: int

    class Config:
        from_attributes = True