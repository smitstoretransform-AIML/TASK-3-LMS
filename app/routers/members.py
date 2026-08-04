from datetime import datetime, timezone
from math import ceil

from fastapi import (
    APIRouter,
    Depends,
    Query,
    BackgroundTasks
)
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission

from app.models.members import Member
from app.models.users import User

from app.utils.notification_service import (
    create_notification_with_email
)

from app.schemas.members import (
    MemberCreate,
    MemberUpdate
)

from app.utils.response import api_response


router = APIRouter(
    prefix="/members",
    tags=["Members"]
)

@router.post("")
def create_member(
    payload: MemberCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_members")
    )
):

    existing_member = db.query(Member).filter(
        Member.email == payload.email,
        Member.deleted_at.is_(None)
    ).first()

    if existing_member:
        return api_response(
            code=400,
            status="Error",
            message="Email already exists",
            data=None
        )

    member = Member(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        address=payload.address,
        membership_date=payload.membership_date,
        created_by=current_user.id
    )

    db.add(member)

    # notification = Notification(
    # user_id=current_user.id,
    # title="New Member Registered",
    # message=f"Member '{member.name}' (ID: {member.id}) has been registered successfully.",
    # type="member_registered",
    # created_by=current_user.id
    # )

    # db.add(notification)

    db.commit()
    db.refresh(member)

    create_notification_with_email(
    db=db,
    background_tasks=background_tasks,
    user_id=current_user.id,
    email=member.email,
    title="Welcome to Library",
    message=(
        f"Hello {member.name},\n\n"
        f"Welcome to our library system.\n"
        f"Your member ID is {member.id}.\n"
        f"Membership date: {member.membership_date}.\n\n"
        f"Happy reading 📚"
    ),
    notification_type="member_registered",
    created_by=current_user.id
)

    db.commit()

    return api_response(
    code=201,
    status="Success",
    message="Member created successfully",
    data={
        "id": member.id,
        "name": member.name,
        "email": member.email,
        "phone": member.phone,
        "address": member.address,
        "membership_date": str(member.membership_date),
        "created_by": member.created_by,
        "updated_by": member.updated_by
    }
)

# GET ALL MEMBERS

@router.get("")
def get_members(
    search: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_members")
    )
):

    query = db.query(Member).filter(
        Member.deleted_at.is_(None)
    )

    if search:
        query = query.filter(
            or_(
                Member.name.ilike(f"%{search}%"),
                Member.email.ilike(f"%{search}%"),
                Member.phone.ilike(f"%{search}%")
            )
        )

    sort_column = getattr(
        Member,
        sort_by,
        Member.id
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

    members = query.offset(
        (page - 1) * limit
    ).limit(limit).all()

    items = []

    for member in members:

        items.append(
            {
                "id": member.id,
                "name": member.name,
                "email": member.email,
                "phone": member.phone,
                "address": member.address,
                "membership_date": str(
                    member.membership_date
                ),
                "created_by": member.created_by,
                "updated_by": member.updated_by
            }
        )

    return api_response(
        code=200,
        status="Success",
        message="Members fetched successfully",
        data={
            "items": items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": ceil(
                    total / limit
                )
            }
        }
    )


# GET MEMBER BY ID

@router.get("/{member_id}")
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_members")
    )
):

    member = db.query(Member).filter(
        Member.id == member_id,
        Member.deleted_at.is_(None)
    ).first()

    if not member:
        return api_response(
            code=404,
            status="Error",
            message="Member not found",
            data=None
        )

    return api_response(
        code=200,
        status="Success",
        message="Member fetched successfully",
        data={
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "phone": member.phone,
            "address": member.address,
            "membership_date": str(
                member.membership_date
            ),
            "created_by": member.created_by,
            "updated_by": member.updated_by
        }
    )


# UPDATE MEMBER

@router.put("/{member_id}")
def update_member(
    member_id: int,
    payload: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_members")
    )
):

    member = db.query(Member).filter(
        Member.id == member_id,
        Member.deleted_at.is_(None)
    ).first()

    if not member:
        return api_response(
            code=404,
            status="Error",
            message="Member not found",
            data=None
        )

    if payload.email:

        existing_member = db.query(Member).filter(
            Member.email == payload.email,
            Member.id != member_id,
            Member.deleted_at.is_(None)
        ).first()

        if existing_member:
            return api_response(
                code=400,
                status="Error",
                message="Email already exists",
                data=None
            )

    update_data = payload.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(member, key, value)

    member.updated_by = current_user.id

    db.commit()
    db.refresh(member)

    return api_response(
        code=200,
        status="Success",
        message="Member updated successfully",
        data={
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "phone": member.phone,
            "address": member.address,
            "membership_date": str(
                member.membership_date
            ),
            "created_by": member.created_by,
            "updated_by": member.updated_by
        }
    )


# DELETE MEMBER

@router.delete("/{member_id}")
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_members")
    )
):

    member = db.query(Member).filter(
        Member.id == member_id,
        Member.deleted_at.is_(None)
    ).first()

    if not member:
        return api_response(
            code=404,
            status="Error",
            message="Member not found",
            data=None
        )

    member.deleted_at = datetime.now(
        timezone.utc
    )

    member.updated_by = current_user.id

    db.commit()

    return api_response(
        code=200,
        status="Success",
        message="Member deleted successfully",
        data=None
    )