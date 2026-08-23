import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Fixed test credentials — signup is ignored if user already exists
TEST_EMAIL = "integration_test@example.com"
TEST_PASSWORD = "testpass123"

# uuid4() generates a new random ID every time pytest imports this file
UNIQUE_PREFIX = str(uuid.uuid4())[:8]

#____________ Fixtures _________________________________

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def auth_token(client):
    # Try signup — 400 is OK if user already exists from a previous test run
    client.post("/v1/users/", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })

    # Login — this always gives us a fresh token
    response = client.post(
        "/v1/auth/login",
        data = {"username": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


# __________ Public route tests ______________________

def test_get_books_is_public(client):
    response = client.get("/v1/books/")

    assert response.status_code == 200
    data = response.json()
    # Pagination fields must be present
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data


def test_get_nonexistent_book_returns_404_with_error_shape(client):
    response = client.get("/v1/books/9999")

    assert response.status_code == 404
    data = response.json()

    assert "error" in data 
    assert "code" in data
    assert data["code"] == "BOOK_NOT_FOUND"


#____________ Auth required tests __________________________


def test_create_book_without_auth_returns_401(client):
    response = client.post("/v1/books/", json = {
        "title": "Should Fail", "author": "Author", "pages": 100
    })

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert "code" in data


def test_create_book_with_auth_returns_201(client, auth_headers):
    response = client.post("v1/books/", json = {
        "title": f"Test Book {UNIQUE_PREFIX}",
        "author": "Test Author",
        "pages": 200
    }, headers = auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == f"Test Book {UNIQUE_PREFIX}"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
    assert "id" in data
    assert "owner_id" in data


#__________ Business Logic _________________
# Checking - Two books cannot have same title
def test_title_returns_400_with_correct_code(client, auth_headers):
    title = f" Duplicate Book {UNIQUE_PREFIX}"

    # Create first time — should succeed
    first = client.post("/v1/books/", json ={
        "title": title,
        "author": "Author",
        "pages": 100
    }, headers = auth_headers)

    assert first.status_code == 201

    # Create second time with same title — should fail
    response = client.post("/v1/books/", json={
        "title": title,
        "author": "Author",
        "pages": 100
    }, headers = auth_headers)

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "DUPLICATE_TITLE"
    assert "error" in data


def test_edit_other_users_book_returns_403_with_correct_code(client, auth_headers):
    # Step 1 — create a book as the main test user
    create_response = client.post("/v1/books/", json={
        "title": f"Owner Book {UNIQUE_PREFIX}",
        "author": "Owner",
        "pages": 100
    }, headers = auth_headers)

    assert create_response.status_code == 201, f"Book creation failed: {create_response.json()}"
    book_id = create_response.json()["id"]

    # Step 2 — create a second user
    other_email = f"other_{UNIQUE_PREFIX}@example.com"
    signup_response = client.post("/v1/users/", json={
        "email": other_email,
        "password": "testpass123"
    })

    assert signup_response.status_code in (201, 400), \
        f"Unexpected signup error: {signup_response.json()}"

    login_response = client.post("/v1/auth/login", data={
        "username": other_email,
        "password": "testpass123"
    })
    assert login_response.status_code == 200, \
        f"Second user login failed: {login_response.json()}"
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    # step 3 - try to edit the first user's book as the second user

    response = client.put(f"/v1/books/{book_id}", json={
        "title": "Hacked Title"
    }, headers = other_headers)

    assert response.status_code == 403, \
    f"Expected 403, got {response.status_code}: {response.json()}"
    data = response.json()
    assert data["code"] == "NOT_OWNER"
    assert "error" in data


def test_owner_can_delete_own_book(client, auth_headers):
    create_response = client.post("/v1/books/", json={
        "title": f"Book to delete {UNIQUE_PREFIX}",
        "author": "Author",
        "pages": 100
    }, headers = auth_headers)

    assert create_response.status_code == 201
    book_id = create_response.json()["id"]

    # delete it
    delete_response = client.delete(f"/v1/books/{book_id}", headers = auth_headers)
    assert delete_response.status_code == 200

    # Verify it's actually gone
    get_response = client.get(f"/v1/books/{book_id}")
    assert get_response.status_code == 404
    assert get_response.json()["code"] == "BOOK_NOT_FOUND"


def test_invalid_login_returns_401_with_correct_code(client):
    response = client.post("/v1/auth/login", data={
        "username": "nonexistent@example.com",
        "password": "wrongpass"
    })

    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "INVALID_CREDENTIALS"
    assert "error" in data