import json 
from app.cache.redis_client import redis_client

ALL_BOOKS_TTL = 60
SINGLE_BOOK_TTL = 300

# --- READ from cache ---

def get_cached_books(
        page: int,
        size: int,
        author: str | None = None
        ) -> dict | None:
    
    key = f"books:all:page={page}:size={size}:author={author or 'none'}"

    try:
        cached = redis_client.get(key)
        if cached:
            print(f"CACHE HIT - {key}")
            return json.loads(cached)
    except Exception as e:
        print(f"Redis unavailable (get_cached_books): {e}")
        
    print(f"CACHE MISS - {key}")
    return None

def get_cached_book(book_id: int) -> dict | None:
    key = f"books:hash:{book_id}"

    try:
        data = redis_client.hgetall(key)
        if data:
            print(f"CACHE HIT - {key}")
            return {
                "id": int(data["id"]),
                "title" : data["title"],
                "author" : data["author"],
                "pages" : int(data["pages"]),
                "owner_id" : int(data["owner_id"])
                }
    except Exception as e:
        print(f"Redis unavailable (get_cached_book): {e}")

    print(f"CACHE MISS -  {key}")
    return None 


# --- WRITE to cache ---

def set_cached_books(
        books_data: dict,
        page: int,
        size:int, 
        author: str | None = None
        ) -> None:
    
    key = f"books:all:page={page}:size={size}:author={author or 'none'}"
    try:
        redis_client.set(key, json.dumps(books_data), ex=ALL_BOOKS_TTL)
    except Exception as e:
        print(f"Redis unavailable (set_cached_books): {e}")

def set_cached_book(book_id: int, book_data: dict) -> None:
    key = f"books:hash:{book_id}"
    try:
        redis_client.hset(key, mapping={
            "id": book_data["id"],
            "title": book_data["title"],
            "author": book_data["author"],
            "pages": book_data["pages"],
            "owner_id": book_data["owner_id"]
        })
        redis_client.expire(key, SINGLE_BOOK_TTL)
    except Exception as e:
        print(f" Redis unavailable (set_cached_book): {e}")

# --- INVALIDATE cache ---

def invalidate_book(book_id:int) -> None:
    try:
        deleted = redis_client.delete(f"books:hash:{book_id}")
        if deleted:
            print(f"Invalidted hash key - books:hash:{book_id}")

        list_keys = redis_client.keys("books:all:*")
        if list_keys:
            redis_client.delete(*list_keys)
            print(f"Invalidated {len(list_keys)} list cache key(s)")
    except Exception as e:
        print(f"Redis unavailable (invalidate_book): {e}")
