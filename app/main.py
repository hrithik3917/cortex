from fastapi import FastAPI
from database import Base, engine
from cache.redis_client import redis_client
from contextlib import asynccontextmanager
from routes.book import router as book_router
from routes.user import router as user_router
from routes.auth import router as auth_router


Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        redis_client.ping()
        print("Redis connection verified")
    except Exception as e:
        print(f" Redis not available: {e}")

    yield

    print("Shutting down - closing redis connection")
    redis_client.close()
    

app = FastAPI(title="Book API", lifespan=lifespan)

app.include_router(book_router, prefix="/v1")
app.include_router(user_router, prefix="/v1")
app.include_router(auth_router, prefix="/v1")

@app.get("/")
def root():
    return {"message": "This Book API is running"}