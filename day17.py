import redis 
import os

redis_client = redis.Redis(
    host = "localhost",
    port= 6379,
    deccode_response = True
)

# Save the book
redis_client.hset(
    "book:1",
    mapping={
        "title": "Atomi Habits",
        "Author": "James",
        "Pages": 320,
        "owner_id": 7
    }

)
# get only the title
title = redis_client.hget("books:1", "title")
print(title)

# get only owner id
owner_id = redis_client.hget("books:1", "owner_id")
print("owner_id:", owner_id)

# get the complete book
book = redis_client.hgetall("books:1")
print(book)