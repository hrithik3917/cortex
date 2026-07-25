from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.book import (
    get_all_books,
    get_book_by_id,
    get_book_by_title,
    insert_book as insert_book_model,
    update_book,
    delete_book,
)
from schemas.book import Bookcreate, BookUpdate, BookResponse
from models.user import User
from cache.book_cache import (
    get_cached_book, 
    get_cached_books,
    set_cached_book,
    set_cached_books,
    invalidate_book
)

def fetch_all_books(db: Session, author : str | None = None) -> list:
    # Step 1 — check cache
    cached = get_cached_books(author)
    if cached is not None:
        return cached
    
    # Step 2 — cache miss: query Postgres
    books = get_all_books(db)
    if author:
        books = [b for b in books if author.lower() in b.author.lower()]

     # Step 3 — serialize and store in cache
    # model_validate converts SQLAlchemy object → Pydantic, model_dump → plain dict
    
    books_data = [BookResponse.model_validate(b).model_dump() for b in books]
    set_cached_books(books_data, author)

    return books


def fetch_book(db: Session, book_id:int):

    cached = get_cached_book(book_id)
    if cached is not None:
        return cached
    

    book = get_book_by_id(book_id, db)
    if not book:
        raise HTTPException(status_code=404, detail=f" book {book_id} Not Found")
    

    book_data = BookResponse.model_validate(book).model_dump()
    set_cached_book(book_id, book_data)
    
    return book


def insert_book(db: Session, book_data: Bookcreate, current_user:User):
    if get_book_by_title(book_data.title, db):
        raise HTTPException(status_code=400, detail=f"Book with title '{book_data.title}' already exists")
    
    data = book_data.model_dump()
    data["owner_id"] = current_user.id
    book = insert_book_model(db, data)

    # Invalidate all list caches — the list just changed
    invalidate_book(book.id)
    return book


def modify_book(db: Session, book_id: int, modified_data: BookUpdate, current_user: User):
    book = fetch_book(db, book_id)

    # fetch_book may return a cached dict — ownership check needs the owner_id
    owner_id = book["owner_id"] if isinstance(book, dict) else book.owner_id
    if owner_id != current_user.id:
        raise HTTPException(status_code=403, detail=" You can only edit your own books")
    
    updated_book = update_book(book_id, db, modified_data.model_dump())

    invalidate_book(book_id)

    return updated_book



def remove_book(db: Session, book_id: int, current_user: User) -> None:
    book = fetch_book(db, book_id)

    owner_id = book["owner_id"] if isinstance(book, dict) else book.owner_id
    if owner_id != current_user.id:
        raise HTTPException(status_code=403, detail=" You can only delete your own books")
    
    invalidate_book(book_id)

    delete_book(book_id, db)