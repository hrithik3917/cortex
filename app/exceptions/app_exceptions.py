from fastapi import HTTPException

# ─── HTTPException subclasses ─────────────────────────────────────────

class BookNotFoundException(HTTPException):
    def __init__(self, book_id: int):
        super().__init__(
            status_code = 404,
            detail = {"error": f"Book {book_id} not found", "code": "BOOK_NOT_FOUND"}
        )


class DuplicateTitleException(HTTPException):
    def __init__(self, title: str):
        super().__init__(
            status_code = 400,
            detail = {"error": f"Book with title '{title}' already exists", "code": "DUPLICATE_TITLE"}
        )


class NotOwnerException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code = 403,
            detail = {"error": "You can only modify your own books", "code": "NOT_OWNER"} 
        )


class UserNotFoundException(HTTPException):
    def __init__(self, user_id):
        super().__init__(
            status_code = 404,
            detail = {"error": f"User '{user_id}' not found" if user_id else "User not found", "code": "USER_NOT_FOUND"}
        )


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code = 401,
            detail = {"error": "Token is invalid or has expired", "code": "INVALID_TOKEN"}
        )



class InvalidCredentialsExceptions(HTTPException):
    def __init__(self):
        super().__init__(
            status_code = 401,
            detail = {"error": "Invalid email or password", "code": "INVALID_CREDENTIALS"}
        )


class EmailAlreadyRegisteredException(HTTPException):
    def __init__(self, email:str):
        super().__init__(
            status_code = 400,
            detail = {"error": f"Email '{email}' is already registered", "code": "EMAIL_ALREADY_REGISTERED"}
        )


# ─── Plain Python exceptions (not HTTPException) ─────────────────────
# These need explicit handlers in main.py because FastAPI doesn't
# handle plain Python exceptions automatically.


class DatabaseUnavailableException(Exception):
    """Raised when the postgres connection fails"""
    pass


class ExternalServiceException(Exception):
    """Raised when Redis, an LLM API, or any downstream service fails"""
    def __init__(self, service: str):
        self.service = service
        super().__init__(f" External service '{service}' failed")