from datetime import datetime, timezone
from math import ceil

from fastapi import (
    APIRouter,
    Depends,
    Query,
    BackgroundTasks
)
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission

from app.utils.notification_service import (
    create_notification_with_email
)

from app.models.fines import Fine
from app.models.members import Member
from app.models.users import User
from app.models.notifications import Notification

from app.utils.response import api_response


router = APIRouter(
    prefix="/fines",
    tags=["Fines"]
)


# GET ALL FINES


@router.get("")
def get_fines(
    status: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_fines")
    )
):

    query = db.query(
        Fine,
        Member
    ).join(
        Member,
        Fine.member_id == Member.id
    ).filter(
        Fine.deleted_at.is_(None)
    )

    if status:
        query = query.filter(
            Fine.status.ilike(status)
        )

    sort_column = getattr(
        Fine,
        sort_by,
        Fine.id
    )

    if sort_order.lower() == "desc":
        query = query.order_by(
            desc(sort_column)
        )
    else:
        query = query.order_by(
            asc(sort_column)
        )

    total = query.count()

    results = query.offset(
        (page - 1) * limit
    ).limit(limit).all()

    items = []

    for fine, member in results:

        items.append(
            {
                "id": fine.id,
                "borrow_record_id": fine.borrow_record_id,
                "member_id": member.id,
                "member_name": member.name,
                "late_days": fine.late_days,
                "fine_amount": fine.fine_amount,
                "status": fine.status,
                "paid_at": fine.paid_at,
                "created_by": fine.created_by
            }
        )

    return api_response(
        code=200,
        status="Success",
        message="Fines fetched successfully",
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


# GET FINE BY ID


@router.get("/{fine_id}")
def get_fine(
    fine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("view_fines")
    )
):

    result = db.query(
        Fine,
        Member
    ).join(
        Member,
        Fine.member_id == Member.id
    ).filter(
        Fine.id == fine_id,
        Fine.deleted_at.is_(None)
    ).first()

    if not result:
        return api_response(
            code=404,
            status="Error",
            message="Fine not found",
            data=None
        )

    fine, member = result

    return api_response(
        code=200,
        status="Success",
        message="Fine fetched successfully",
        data={
            "id": fine.id,
            "borrow_record_id": fine.borrow_record_id,
            "member_id": member.id,
            "member_name": member.name,
            "late_days": fine.late_days,
            "fine_amount": fine.fine_amount,
            "status": fine.status,
            "paid_at": fine.paid_at,
            "created_by": fine.created_by
        }
    )


# PAY FINE


@router.post("/{fine_id}/pay")
def pay_fine(
    fine_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_fines")
    )
):

    fine = db.query(Fine).filter(
        Fine.id == fine_id,
        Fine.deleted_at.is_(None)
    ).first()

    if not fine:
        return api_response(
            code=404,
            status="Error",
            message="Fine not found",
            data=None
        )

    if fine.status == "paid":
        return api_response(
            code=400,
            status="Error",
            message="Fine already paid",
            data=None
        )

    fine.status = "paid"
    fine.paid_at = datetime.now(
        timezone.utc
    )

    member = db.query(Member).filter(
        Member.id == fine.member_id
    ).first()

    create_notification_with_email(
        db=db,
        background_tasks=background_tasks,
        user_id=current_user.id,
        email=member.email,
        title="Fine Paid",
        message=(
            f"Hello {member.name}, "
            f"your fine of ₹{fine.fine_amount} "
            f"has been paid successfully."
        ),
    notification_type="fine_paid",
    created_by=current_user.id
)  

    db.commit()
    db.refresh(fine)

    return api_response(
        code=200,
        status="Success",
        message="Fine paid successfully",
        data={
            "id": fine.id,
            "borrow_record_id": fine.borrow_record_id,
            "member_id": fine.member_id,
            "late_days": fine.late_days,
            "fine_amount": fine.fine_amount,
            "status": fine.status,
            "paid_at": fine.paid_at,
            "created_by": fine.created_by
        }
    )