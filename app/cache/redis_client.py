import redis
import os
from dotenv import load_dotenv
from redis.backoff import NoBackoff
from redis.retry import Retry

load_dotenv()

# Single redis connection used across the whole app
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,          # This returns str instead of bytes
    socket_connect_timeout=2,
    socket_timeout=2,
    retry=Retry(NoBackoff(), 0),    # fail fast instead of retrying a dead connection
    retry_on_timeout=False,
    retry_on_error=[],
    )