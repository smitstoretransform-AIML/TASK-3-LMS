from datetime import datetime, timezone
from math import ceil

from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.core.security import hash_password

from app.models.users import User
from app.models.roles import Role

from app.schemas.users import (
    UserCreate,
    UserUpdate,
    UserRoleUpdate
)

from app.utils.response import api_response


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# CREATE USER


@router.post("")
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_users")
    )
):

    existing_user = db.query(User).filter(
        User.email == payload.email,
        User.deleted_at.is_(None)
    ).first()

    if existing_user:
        return api_response(
            code=400,
            status="Error",
            message="Email already exists",
            data=None
        )

    member_role = db.query(Role).filter(
        Role.name == "Member"
    ).first()

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role_id=member_role.id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return api_response(
        code=201,
        status="Success",
        message="User created successfully",
        data={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": member_role.name
        }
    )


# GET ALL USERS


@router.get("")
def get_users(
    search: str = None,
    role: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_users")
    )
):

    query = db.query(User, Role).join(
        Role,
        User.role_id == Role.id
    ).filter(
        User.deleted_at.is_(None)
    )

    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    if role:
        query = query.filter(
            Role.name.ilike(role)
        )

    sort_column = getattr(
        User,
        sort_by,
        User.id
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

    for user, role in results:

        items.append(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": role.name
            }
        )

    return api_response(
        code=200,
        status="Success",
        message="Users fetched successfully",
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


# GET USER BY ID


@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_users")
    )
):

    result = db.query(
        User,
        Role
    ).join(
        Role,
        User.role_id == Role.id
    ).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()

    if not result:
        return api_response(
            code=404,
            status="Error",
            message="User not found",
            data=None
        )

    user, role = result

    return api_response(
        code=200,
        status="Success",
        message="User fetched successfully",
        data={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": role.name
        }
    )


# UPDATE USER


@router.put("/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_users")
    )
):

    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()

    if not user:
        return api_response(
            code=404,
            status="Error",
            message="User not found",
            data=None
        )

    if payload.email:

        existing_user = db.query(User).filter(
            User.email == payload.email,
            User.id != user_id,
            User.deleted_at.is_(None)
        ).first()

        if existing_user:
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
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    role = db.query(Role).filter(
        Role.id == user.role_id
    ).first()

    return api_response(
        code=200,
        status="Success",
        message="User updated successfully",
        data={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": role.name
        }
    )



@router.patch("/{user_id}/role")
def change_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_users")
    )
):

    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()

    if not user:
        return api_response(
            code=404,
            status="Error",
            message="User not found",
            data=None
        )

    # Target user's role
    target_role = db.query(Role).filter(
        Role.id == user.role_id
    ).first()

    # Current admin's role
    current_role = db.query(Role).filter(
        Role.id == current_user.role_id
    ).first()

    # Admin cannot change their own role
    if user.id == current_user.id:
        return api_response(
            code=400,
            status="Error",
            message="You cannot change your own role",
            data=None
        )

    # Admin cannot change another admin's role
    if target_role.name.lower() == "admin":
        return api_response(
            code=403,
            status="Error",
            message="You cannot change another admin's role",
            data=None
        )

    role = db.query(Role).filter(
        Role.name == payload.role.capitalize()
    ).first()

    if not role:
        return api_response(
            code=404,
            status="Error",
            message="Role not found",
            data=None
        )

    user.role_id = role.id

    db.commit()
    db.refresh(user)

    return api_response(
        code=200,
        status="Success",
        message="User role updated successfully",
        data={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": role.name
        }
    )

# DELETE USER


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("manage_users")
    )
):

    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()

    if not user:
        return api_response(
            code=404,
            status="Error",
            message="User not found",
            data=None
        )

    if user.id == current_user.id:
        return api_response(
            code=400,
            status="Error",
            message="You cannot delete yourself",
            data=None
        )

    user.deleted_at = datetime.now(
        timezone.utc
    )

    db.commit()

    return api_response(
        code=200,
        status="Success",
        message="User deleted successfully",
        data=None
    )