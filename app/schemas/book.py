from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class Bookcreate(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    pages: int = Field(..., ge=1)
    owner_id: Optional[int] = None


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1)
    pages: Optional[int] = Field(None, ge=1)


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    pages: int
    owner_id: Optional[int] = None


class MessageResponse(BaseModel):
    message: str
