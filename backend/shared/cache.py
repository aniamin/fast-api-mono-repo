"""Redis caching helpers."""
from typing import Optional

from redis import Redis

from .config import settings

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def _resource_key(resource_id: str) -> str:
    return f"resource:{resource_id}"


def get_cached_resource(resource_id: str) -> Optional[str]:
    return redis_client.get(_resource_key(resource_id))


def set_cached_resource(resource_id: str, value: str, ttl: int = 60) -> None:
    redis_client.set(_resource_key(resource_id), value, ex=ttl)


def invalidate_resource(resource_id: str) -> None:
    redis_client.delete(_resource_key(resource_id))


__all__ = [
    "get_cached_resource",
    "set_cached_resource",
    "invalidate_resource",
    "redis_client",
]
