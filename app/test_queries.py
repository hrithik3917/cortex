"""
Standalone script demonstrating the 3 required SQLAlchemy relationship queries.
Run from the week1_practise directory:
    python -m book_api.test_queries
"""
from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.book import Book

Base.metadata.create_all(bind=engine)


def run():
    db = SessionLocal()
    try:
        # ── Setup ─────────────────────────────────────────────────────────────
        user = User(email="alice@example.com", hashed_password="hashed_secret")
        db.add(user)
        db.commit()
        db.refresh(user)

        db.add_all([
            Book(title="Clean Code", author="Robert Martin", pages=431, owner_id=user.id),
            Book(title="The Pragmatic Programmer", author="Hunt & Thomas", pages=352, owner_id=user.id),
        ])
        db.commit()
        print(f"Setup complete — user id={user.id}, 2 books created.\n")

        # ── Query 1: Get all books belonging to user with id=1 ────────────────
        # Uses a simple filter on the FK column (no relationship traversal needed)
        books = db.query(Book).filter(Book.owner_id == user.id).all()
        print("Query 1 — Books belonging to user via FK filter:")
        for b in books:
            print(f"  {b.title!r} by {b.author}")

        # ── Query 2: Access user.books via the relationship ───────────────────
        # SQLAlchemy lazy-loads the books list when we access .books
        fetched = db.query(User).filter(User.id == user.id).first()
        print(f"\nQuery 2 — user.books relationship on {fetched.email!r}:")
        for b in fetched.books:
            print(f"  {b.title!r} (id={b.id})")

        book_ids = [b.id for b in fetched.books]

        # ── Query 3: Delete user, verify cascade deletes their books ──────────
        db.delete(fetched)
        db.commit()
        print("\nQuery 3 — After deleting user, checking cascade on books:")
        for bid in book_ids:
            still_exists = db.query(Book).filter(Book.id == bid).first()
            status = "DELETED ✓" if still_exists is None else "STILL EXISTS ✗"
            print(f"  Book id={bid}: {status}")

    finally:
        db.close()


if __name__ == "__main__":
    run()
