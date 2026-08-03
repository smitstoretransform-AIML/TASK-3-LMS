from datetime import date

from pydantic import (
    BaseModel,
    EmailStr,
    field_validator
)


class MemberCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    membership_date: date

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):

        value = value.strip()

        if len(value) < 3:
            raise ValueError(
                "Name must contain at least 3 characters"
            )

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str):

        value = value.strip()

        if not value.isdigit():
            raise ValueError(
                "Phone number must contain only digits"
            )

        if len(value) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )

        return value

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str):

        value = value.strip()

        if len(value) < 5:
            raise ValueError(
                "Address is too short"
            )

        return value


class MemberUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    membership_date: date | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):

        if value is None:
            return value

        value = value.strip()

        if len(value) < 3:
            raise ValueError(
                "Name must contain at least 3 characters"
            )

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):

        if value is None:
            return value

        value = value.strip()

        if not value.isdigit():
            raise ValueError(
                "Phone number must contain only digits"
            )

        if len(value) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )

        return value


class MemberResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    address: str
    membership_date: date

    class Config:
        from_attributes = True