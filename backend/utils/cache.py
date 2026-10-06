import json
import redis

redis_client = redis.from_url(
    "redis://localhost:6379/1",
    decode_responses=True
)

TREK_CACHE_TTL = 300  # 5 minutes


def get_cached_treks(key):
    data = redis_client.get(key)

    if data:
        return json.loads(data)

    return None


def cache_treks(key, data):
    redis_client.setex(
        key,
        TREK_CACHE_TTL,
        json.dumps(data)
    )


def clear_trek_cache():
    for key in redis_client.scan_iter(match="treks:*"):
        redis_client.delete(key)