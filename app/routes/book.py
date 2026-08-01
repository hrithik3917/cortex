from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from typing import Optional
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.pagination import PaginatedBooksResponse
from app.schemas.book import Bookcreate, BookUpdate, BookResponse, MessageResponse
from app.services.book_service import (
    fetch_all_books,
    fetch_book,
    insert_book,
    modify_book,
    remove_book,
)

router = APIRouter(
    prefix="/books",
    tags=["Books"]
)



@router.get("/", response_model=PaginatedBooksResponse)
def get_books(
    page: int = Query(default=1, ge=1, description="Page number, starting from 1"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page, max 100"),
    author: Optional[str] = None, 
    db: Session = Depends(get_db)
    ):

    return fetch_all_books(db, page=page, size=size, author=author)      


@router.get("/{book_id}", response_model= BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    return fetch_book(db, book_id)


@router.post("/", response_model=BookResponse, status_code=201)
def add_book(book_data: Bookcreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return insert_book(db, book_data, current_user)


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id:int, book:BookUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return modify_book(db, book_id, book, current_user)


@router.delete("/{book_id}", response_model=MessageResponse)
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    remove_book(db, book_id, current_user)
    return{"message": f"Book {book_id} deleted successfully"}