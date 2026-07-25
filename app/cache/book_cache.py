import json 
from app.cache.redis_client import redis_client

ALL_BOOKS_TTL = 60
SINGLE_BOOK_TTL = 300

# --- READ from cache ---

def get_cached_books(author: str | None = None) -> list | None:
    key = f"books:all:{author or 'none'}"
    cached = redis_client.get(key)

    if cached:
        print(f"CACHE HIT - {key}")
        return json.loads(cached)
    print(f"CACHE MISS - {key}")
    return None

def get_cached_book(book_id: int) -> dict | None:
    key = f"books:hash:{book_id}"

    data = redis_client.hgetall(key)

    if not data:
        print(f"CACHE MISS -  {key}")
        return None

    print(f"CACHE HIT - {key}")

    return {
        "id": int(data["id"]),
        "title" : data["title"],
        "author" : data["author"],
        "pages" : int(data["pages"]),
        "owner_id" : int(data["owner_id"])
    }


# --- WRITE to cache ---

def set_cached_books(books_data: list, author: str | None = None) -> None:
    key = f"books:all:{author or 'none'}"
    redis_client.setex(key, ALL_BOOKS_TTL, json.dumps(books_data))

def set_cached_book(book_id: int, book_data: dict) -> None:
    key = f"books:hash:{book_id}"
    redis_client.hset(key, mapping={
        "id": book_data["id"],
        "title": book_data["title"],
        "author": book_data["author"],
        "pages": book_data["pages"],
        "owner_id": book_data["owner_id"]
    })
    redis_client.expire(key, SINGLE_BOOK_TTL)

# --- INVALIDATE cache ---

def invalidate_book(book_id:int) -> None:
    deleted = redis_client.delete(f"books:hash:{book_id}")
    if deleted:
        print(f"Invalidted hash key - books:hash:{book_id}")

    list_keys = redis_client.keys("books:all:*")
    if list_keys:
        redis_client.delete(*list_keys)
        print(f"Invalidated {len(list_keys)} list cache key(s)")
