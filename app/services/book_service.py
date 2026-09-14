from sqlalchemy.orm import Session

from app.cache.book_cache import (
    get_cached_book,
    get_cached_books,
    invalidate_book,
    set_cached_book,
    set_cached_books,
)
from app.exceptions.app_exceptions import (
    BookNotFoundException,
    DuplicateTitleException,
    NotOwnerException,
)
from app.models.book import (
    delete_book,
    get_all_books,
    get_book_by_id,
    get_book_by_title,
    update_book,
)
from app.models.book import (
    insert_book as insert_book_model,
)
from app.models.user import User
from app.schemas.book import Bookcreate, BookResponse, BookUpdate


def fetch_all_books(
    db: Session, page: int = 1, size: int = 10, author: str | None = None
) -> dict:
    # Step 1 — check cache
    cached = get_cached_books(page, size, author)
    if cached is not None:
        return cached

    # Step 2 — cache miss: query Postgres with pagination
    skip = (page - 1) * size
    books, total = get_all_books(db, skip=skip, limit=size, author=author)

    # Step 3 — serialize and store in cache
    # model_validate converts SQLAlchemy object → Pydantic, model_dump → plain dict

    books_data = [BookResponse.model_validate(b).model_dump() for b in books]
    total_pages = -(-total // size) if total > 0 else 1

    result = {
        "items": books_data,
        "total": total,
        "page": page,
        "size": size,
        "pages": total_pages,
    }

    set_cached_books(result, page, size, author)

    return result


def fetch_book(db: Session, book_id: int):

    cached = get_cached_book(book_id)
    if cached is not None:
        return cached

    book = get_book_by_id(book_id, db)
    if not book:
        raise BookNotFoundException(book_id)

    book_data = BookResponse.model_validate(book).model_dump()
    set_cached_book(book_id, book_data)

    return book


def insert_book(db: Session, book_data: Bookcreate, current_user: User):
    if get_book_by_title(book_data.title, db):
        raise DuplicateTitleException(book_data.title)

    data = book_data.model_dump()
    data["owner_id"] = current_user.id
    book = insert_book_model(db, data)

    # Invalidate all list caches — the list just changed
    invalidate_book(book.id)
    return book


def modify_book(
    db: Session, book_id: int, modified_data: BookUpdate, current_user: User
):
    book = fetch_book(db, book_id)

    # fetch_book may return a cached dict — ownership check needs the owner_id
    owner_id = book["owner_id"] if isinstance(book, dict) else book.owner_id
    if owner_id != current_user.id:
        raise NotOwnerException()

    updated_book = update_book(book_id, db, modified_data.model_dump())

    invalidate_book(book_id)

    return updated_book


def remove_book(db: Session, book_id: int, current_user: User) -> None:
    book = fetch_book(db, book_id)

    owner_id = book["owner_id"] if isinstance(book, dict) else book.owner_id
    if owner_id != current_user.id:
        raise NotOwnerException()

    invalidate_book(book_id)

    delete_book(book_id, db)
