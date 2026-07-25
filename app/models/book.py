from app.database import Base
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from typing import Optional


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
    owner_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    # String ref "User" — SQLAlchemy resolves this lazily, no import needed
    owner = relationship("User", back_populates="books")

    def __repr__(self):
        return f"title={self.title}, author={self.author}"
    

def get_all_books(db:Session) -> list[Book]:
    return db.query(Book).all()


def get_book_by_id(book_id:int, db: Session) -> Optional[Book]:
    return db.query(Book).filter(Book.id == book_id).first()


def get_book_by_title(title: str, db: Session) -> Optional[Book]:
    return db.query(Book).filter(Book.title.ilike(title)).first()


def insert_book(db: Session, book_data) -> Book:
    payload = book_data.model_dump() if hasattr(book_data, "model_dump") else dict(book_data)
    book = Book(**payload)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book(book_id: int, db: Session, updates: dict) -> Book:
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise ValueError(f"Book {book_id} not found")

    for key, value in updates.items():
        if value is not None:
            setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book


def delete_book(book_id: int, db: Session) -> None:
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise ValueError(f"Book {book_id} not found")

    db.delete(book)
    db.commit()

