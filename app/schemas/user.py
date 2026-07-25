from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime
from app.schemas.book import BookResponse


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_active: bool
    created_at: datetime


class UserWithBooks(UserResponse):
    books: list[BookResponse] = [] 

