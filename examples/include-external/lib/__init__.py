"""Library that uses cachetools to test include_external."""

from cachetools import LRUCache

cache: LRUCache[str, int] = LRUCache(maxsize=100)


def get_cached(key: str) -> int | None:
    """Get a value from the cache."""
    return cache.get(key)


def set_cached(key: str, value: int) -> None:
    """Set a value in the cache."""
    cache[key] = value
