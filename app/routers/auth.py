from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.models.users import User
from app.schemas.users import UserCreate, UserResponse

# pyrefly: ignore [missing-import]
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest


from app.utils.response import api_response
from app.core.dependencies import get_current_user
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

#register user

@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user.email,
        User.deleted_at.is_(None)
    ).first()

    if existing_user:
        return api_response(
            code=400,
            status="Error",
            message="Email already exists",
            data=None
        )

    if user.role not in ["admin", "librarian"]:
        return api_response(
            code=400,
            status="Error",
            message="Invalid role",
            data=None
        )

    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return api_response(
    code=201,
    status="Success",
    message="User created successfully",
    data={
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "role": db_user.role
    }
)


#login user

@router.post("/login")
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == credentials.email,
        User.deleted_at.is_(None)
    ).first()

    if not user:
        return api_response(
            code=401,
            status="Error",
            message="Invalid email or password",
            data=None
        )

    if not verify_password(
        credentials.password,
        user.password_hash
    ):
        return api_response(
            code=401,
            status="Error",
            message="Invalid email or password",
            data=None
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return api_response(
        code=200,
        status="Success",
        message="Login successful",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }
    )


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return api_response(
            code=401,
            status="Error",
            message="Invalid or expired token",
            data=None
        )

    return api_response(
        code=200,
        status="Success",
        message="User profile fetched successfully",
        data={
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role
        }
    )