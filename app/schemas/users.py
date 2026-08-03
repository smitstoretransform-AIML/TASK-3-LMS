from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        value = value.strip()

        if len(value) < 3:
            raise ValueError(
                "Name must contain at least 3 characters"
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        value = value.strip()

        if len(value) < 6:
            raise ValueError(
                "Password must contain at least 6 characters"
            )

        return value

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str):
        value = value.strip().lower()

        allowed_roles = [
            "admin",
            "librarian",
            "member"
        ]

        if value not in allowed_roles:
            raise ValueError(
                "Role must be one of: admin, librarian, member"
            )

        return value


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True