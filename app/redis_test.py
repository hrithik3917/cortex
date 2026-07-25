import redis

r = redis.Redis(host="localhost", port=6379, db=0)

r.set("test_key", "hello redis")
value = r.get("test_key")
print(value)                        # b'hello redis' (bytes)
print(value.decode("utf-8"))        # 'hello redis' (string)

r.delete("test_key")
print(r.get("test_key"))            # None — key is gone