import json
import redis
from typing import Optional, Any
from .base import CacheInterface

class RedisCache(CacheInterface):
    def __init__(self, host: str = "localhost", port: int = 6379):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
    
    def get(self, key: str) -> Optional[Any]:
        try:
            data = self.client.get(key)
            return json.loads(str(data)) if data else None
        except (redis.RedisError, json.JSONDecodeError):
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        try:
            self.client.setex(key, ttl, json.dumps(value))
        except redis.RedisError:
            pass  # Fail silently if Redis is unavailable