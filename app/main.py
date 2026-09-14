from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.cache.redis_client import redis_client
from app.database import Base, engine
from app.exceptions.app_exceptions import (
    DatabaseUnavailableException,
    ExternalServiceException,
)
from app.routes.auth import router as auth_router
from app.routes.book import router as book_router
from app.routes.user import router as user_router

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        redis_client.ping()
        print("Redis connection verified")
    except RedisError as e:
        print(f" Redis not available: {e}")

    yield

    print("Shutting down - closing redis connection")
    redis_client.close()


app = FastAPI(title="Book API", lifespan=lifespan)


# ─── Global Exception Handlers ────────────────────────────────────────


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):

    # If the detail is already in {error, code} shape, return it directly
    # This handles all the custom exception classes (BookNotFoundException etc.)
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    # For plain HTTPExceptions (e.g. 401 from OAuth2PasswordBearer),
    # wrap them in our consistent shape
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail), "code": "HTTP_ERROR"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Pydantic 422 errors — reshape to consistent format
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(
            {
                "error": "Request validation failed",
                "code": "VALIDATION_ERROR",
                "details": exc.errors(),
            }
        ),
    )


@app.exception_handler(DatabaseUnavailableException)
async def db_unavailable_handler(request: Request, exc: DatabaseUnavailableException):
    return JSONResponse(
        status_code=503,
        content={
            "error": "Database is temporarily unavailable",
            "code": "DB_UNAVAILABLE",
        },
    )


@app.exception_handler(ExternalServiceException)
async def external_exception_handler(requestL: Request, exc: ExternalServiceException):
    return JSONResponse(
        status_code=502,
        content={
            "error": f"Downstream service '{exc.service}' failed",
            "code": "EXTERNAL_SERVICE_ERROR",
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Catch-all — never expose raw Python errors to clients
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occured", "code": "INTERNAL_ERROR"},
    )


app.include_router(book_router, prefix="/v1")
app.include_router(user_router, prefix="/v1")
app.include_router(auth_router, prefix="/v1")


@app.get("/")
def root():
    return {"message": "This Book API is running"}
