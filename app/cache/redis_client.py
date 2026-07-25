import redis
import os
from dotenv import load_dotenv

load_dotenv()

# Single redis connection used across the whole app
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True           # This returns str instead of bytes    
    )