from pydantic import BaseModel, ConfigDict
from app.schemas.book import BookResponse
from typing import Optional


class PaginatedBooksResponse(BaseModel):
    items: list[BookResponse]     # The books on the current page
    total: int                    # The total number of books matching the query
    page: int                     # The current page number
    size: int                     # The number of books per page
    pages: int                    # The total number of pages available

    model_config = ConfigDict(from_attributes=True)

