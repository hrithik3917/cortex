from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.book import Bookcreate, BookResponse, BookUpdate, MessageResponse
from app.schemas.pagination import PaginatedBooksResponse
from app.services.book_service import (
    fetch_all_books,
    fetch_book,
    insert_book,
    modify_book,
    remove_book,
)

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=PaginatedBooksResponse)
def get_books(
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1, description="Page number, starting from 1"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page, max 100"),
    author: str | None = None,
):

    return fetch_all_books(db, page=page, size=size, author=author)


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Annotated[Session, Depends(get_db)]):
    return fetch_book(db, book_id)


@router.post("/", response_model=BookResponse, status_code=201)
def add_book(
    book_data: Bookcreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return insert_book(db, book_data, current_user)


@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book: BookUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return modify_book(db, book_id, book, current_user)


@router.delete("/{book_id}", response_model=MessageResponse)
def delete_book(
    book_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    remove_book(db, book_id, current_user)
    return {"message": f"Book {book_id} deleted successfully"}
