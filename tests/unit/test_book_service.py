import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.book_service import(
    fetch_all_books,
    fetch_book,
    insert_book,
    modify_book,
    remove_book,
)
from app.schemas.book import BookResponse, Bookcreate, BookUpdate

# ---- Fixtures ------------------------------

@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    return user



# ---- fetch_all_books tests ------------------------------

def test_fetch_all_books_returns_cached_dict_on_hit(mock_db):
    # Scenario: Redis already has this page cached
    # Expected: returns cached dict immediately — Postgres never queried
    cached = {
        "items": [{"id": 1, "title": "Clean Code", "author": "Martin", "pages": 464, "owner_id": 1}],
        "total": 1,  "page": 1, "size": 10, "pages": 1
    }

    with patch("app.services.book_service.get_cached_books", return_value=cached):
        result = fetch_all_books(mock_db, page=1, size=10)
        assert result == cached
        assert result["total"] == 1
        assert result["pages"] == 1


def test_fetch_all_books_queries_db_on_cache_miss(mock_db):
    # Scenario: Redis has nothing — DB returns 1 book
    # Expected: paginated dict built correctly and stored in Redis
    fake_book = MagicMock()
    fake_book.id = 1
    fake_book.title = "Clean Code"
    fake_book.author = "Martin"
    fake_book.pages = 464
    fake_book.owner_id = 1

    with patch("app.services.book_service.get_cached_books", return_value=None):
        with patch("app.services.book_service.get_all_books", return_value=([fake_book], 1)):
            with patch("app.services.book_service.set_cached_books"):
                with patch.object(BookResponse, "model_validate", return_value=BookResponse(
                    id=1, title="Clean Code", author="Martin", pages=464, owner_id=1
                )):
                    result = fetch_all_books(mock_db, page=1, size=10)

                    assert result["total"] == 1
                    assert result["page"] == 1
                    assert result["size"] == 10
                    assert result["pages"] == 1
                    assert len(result["items"]) == 1


def test_fetch_all_books_pagination_math_is_correct(mock_db):
    # Scenario: 25 books total, requesting page 2 with size 10
    # Expected: skip=10, pages=3 (ceiling of 25/10)
    # This test only checks the math — not what DB returns

    fake_books = [MagicMock() for _ in range(10)]   # This created 10 seperate MagicMock objects
    for i, b in enumerate(fake_books):
        b.id = i + 11
        b.title = f"Book {i}"
        b.author = "Author"
        b.pages = 100
        b.owner_id = 1

    with patch("app.services.book_service.get_cached_books", return_value=None):
        with patch("app.services.book_service.get_all_books", return_value=(fake_books, 25)) as mock_query:
            with patch("app.services.book_service.set_cached_books"):
                with patch.object(BookResponse, "model_validate", side_effect= lambda b: BookResponse(
                    id = b.id, title = b.title, author = b.author, pages= b.pages, owner_id = b.owner_id
                )):
                    result = fetch_all_books(mock_db, page=2, size=10)

                    # Verify skip was calculated correctly: (2-1) * 10 = 10
                    mock_query.assert_called_once_with(mock_db, skip=10, limit=10, author=None)

                    assert result["total"] == 25
                    assert result["page"] == 2
                    assert result["size"] == 10
                    assert result["pages"] == 3    # ceiling(25/10) = 3


def test_fetch_all_books_filter_by_author(mock_db):
    # Scenario: author filter passed in — should reach the DB query
    # Expected: author is passed through to get_all_books unchanged
    with patch("app.services.book_service.get_cached_books", return_value=None):
        with patch("app.services.book_service.get_all_books", return_value =([], 0)) as mock_query:
            with patch("app.services.book_service.set_cached_books"):
                fetch_all_books(mock_db, page=1, size=10, author="Martin")

                # Confirm the author filter reached the DB layer
                mock_query.assert_called_once_with(mock_db, skip=0, limit=10, author="Martin")


# ---- fetch_book tests ------------------------------

def test_fetch_book_raises_404_when_not_in_cache_or_db(mock_db):
    # Scenario: Redis has nothing (cache miss), Postgres has nothing (DB miss)
    with patch("app.services.book_service.get_cached_book", return_value=None):
        with patch("app.services.book_service.get_book_by_id", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                fetch_book(mock_db, book_id = 999)
            assert exc_info.value.status_code == 404


def test_fetch_book_returns_cached_dict_on_cache_hit(mock_db):
    # Scenario: Redis has the book (cache hit)
    # Expected: returns the cached dict immediately — Postgres never queried
    cached = {"id": 1, "title": "Clean Code", "author": "Martin", "pages": 464, "owner_id": 1}

    with patch("app.services.book_service.get_cached_book", return_value=cached):
        result = fetch_book(mock_db, book_id=1)
        assert result == cached
        assert result["title"] == "Clean Code"


# ---- create_book tests ------------------------------

def test_insert_book_raises_400_on_duplicate_title(mock_db, mock_user):
    # Scenario: a book with this title already exists in Postgres
    # Expected: 400 HTTPException — duplicate rejected before insert

    book_data = Bookcreate(title="Clean Code", author="Martin", pages=464)
    fake_exisitng = MagicMock()         #It represents the already-exisiting book

    with patch("app.services.book_service.insert_book", return_value=fake_exisitng):
        with pytest.raises(HTTPException) as exc_info:
            insert_book(mock_db, book_data, mock_user)

        assert exc_info.value.status_code == 400


def test_insert_book_succeeds_when_title_is_unique(mock_db, mock_user):
    # Scenario: title doesn't exist yet → book is inserted → cache invalidated
    # Expected: returns the newly inserted book

    book_data = Bookcreate(title="New Book", author="Author", pages=200)
    fake_book = MagicMock()
    fake_book.id = 2

    with patch("app.services.book_service.get_book_by_title", return_value=None):
        with patch("app.services.book_service.insert_book_model", return_value=fake_book):
            with patch("app.services.book_service.invalidate_book"):
                result = insert_book(mock_db, book_data, mock_user)
                assert result == fake_book


# ---- modify_book tests ------------------------------

def test_modify_book_raises_403_when_user_is_not_owner(mock_db, mock_user):
    # Scenario: book's owner_id=999, mock_user.id=1 → mismatch
    # Expected: 403 — can't edit someone else's book

    cached_book = {"id": 1, "title": "Test", "author": "Author", "pages": 100, "owner_id": 999}
    book_data = BookUpdate(title = "New Title")

    with patch("app.services.book_service.get_cached_book", return_value=cached_book):
        with pytest.raises(HTTPException) as exc_info:
            modify_book(mock_db, book_id = 1, modified_data = book_data, current_user = mock_user)

        assert exc_info.value.status_code == 403


def test_modify_book_succeeds_when_user_is_owner(mock_db, mock_user):
    # Scenario: book's owner_id=1, mock_user.id=1 → match
    # Expected: book is updated and returned

    cached_book = {"id": 1, "title": "Test", "author": "Author", "pages": 100, "owner_id": 1}
    fake_updated = MagicMock()
    book_data = BookUpdate(title = "Updated Title")

    with patch("app.services.book_service.get_cached_book", return_value=cached_book):
        with patch("app.services.book_service.update_book", return_value=fake_updated):
            with patch("app.services.book_service.invalidate_book"):
                result = modify_book(mock_db, book_id = 1, modified_data = book_data, current_user = mock_user)
                assert result == fake_updated


# ---- remove_book tests ------------------------------

def test_remove_book_raises_403_when_user_is_not_owner(mock_db, mock_user):
    # Scenario: book's owner_id=999, mock_user.id=1 → mismatch
    # Expected: 403 — can't delete someone else's book

    cached_book = {"id": 1, "title": "Test", "author": "Author", "pages": 100, "owner_id": 999}

    with patch("app.services.book_service.get_cached_book", return_value=cached_book):
        with pytest.raises(HTTPException) as exc_info:
            remove_book(mock_db, book_id = 1, current_user = mock_user)
        assert exc_info.value.status_code == 403


def test_remove_book_succeeds_when_user_is_owner(mock_db, mock_user):
    # Scenario: book's owner_id=1, mock_user.id=1 → match
    # Expected: runs without raising anything — delete and invalidate called

    cached_book = {"id": 1, "title": "Test", "author": "Author", "pages": 100, "owner_id": 1}

    with patch("app.services.book_service.get_cached_book", return_value=cached_book):
        with patch("app.services.book_service.invalidate_book"):
            with patch("app.services.book_service.delete_book"):
                remove_book(mock_db, book_id = 1, current_user = mock_user)
