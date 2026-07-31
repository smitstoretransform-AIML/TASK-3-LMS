from pydantic import BaseModel, EmailStr, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Password is required")

        return value


class Token(BaseModel):
    access_token: str
    token_type: str