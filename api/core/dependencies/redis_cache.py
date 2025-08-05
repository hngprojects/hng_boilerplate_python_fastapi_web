import redis
from api.utils.settings import settings
import logging

_redis_client = None

def get_redis_client():
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.StrictRedis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            _redis_client.ping()  # Test connection first
        except (redis.ConnectionError, redis.AuthenticationError) as e:
            logging.warning(f"Redis connection failed: {e}")
            _redis_client = None  # Reset the client
    return _redis_client
