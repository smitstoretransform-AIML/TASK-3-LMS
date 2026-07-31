from pydantic import BaseModel, field_validator
from typing import Optional

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    category: str
    publisher: Optional[str] = None
    total_copies: int

    @field_validator("title", "author", "category")
    @classmethod
    def validate_text_fields(cls, value: str):
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Field must contain at least 2 characters")

        return value

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, value: str):
        value = value.strip()

        if len(value) < 10:
            raise ValueError("ISBN must contain at least 10 characters")

        return value

    @field_validator("total_copies")
    @classmethod
    def validate_total_copies(cls, value: int):
        if value <= 0:
            raise ValueError(
                "Total copies must be greater than 0"
            )

        return value


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    category: Optional[str] = None
    publisher: Optional[str] = None
    total_copies: Optional[int] = None