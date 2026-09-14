from pydantic import BaseModel, ConfigDict, Field


class Bookcreate(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    pages: int = Field(..., ge=1)
    owner_id: int | None = None


class BookUpdate(BaseModel):
    title: str | None = Field(None, min_length=1)
    author: str | None = Field(None, min_length=1)
    pages: int | None = Field(None, ge=1)


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    pages: int
    owner_id: int | None = None


class MessageResponse(BaseModel):
    message: str
