# Cache utilities for Redis caching

from functools import wraps
from app.extensions import cache


def make_cache_key(prefix, *args, **kwargs):
    """Generate a cache key from prefix and arguments."""
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None)
    return ":".join(key_parts)


def cached_list(prefix, timeout=300):
    """Decorator to cache list query results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = make_cache_key(prefix, "list", *args[1:], **kwargs)
            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout=timeout)
            return result
        return wrapper
    return decorator


def cached_item(prefix, timeout=300):
    """Decorator to cache single item lookups."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # args[0] is self/cls, args[1] is typically the id
            item_id = args[1] if len(args) > 1 else kwargs.get('id')
            cache_key = make_cache_key(prefix, "item", item_id)
            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                if result is not None:
                    cache.set(cache_key, result, timeout=timeout)
            return result
        return wrapper
    return decorator


def invalidate_cache(prefix, item_id=None):
    """
    Invalidate cache entries for a given prefix.
    
    Note: Flask-Caching with SimpleCache/RedisCache doesn't support pattern deletion.
    This function clears specific keys. For production with Redis, consider using
    redis-py directly with SCAN for pattern-based deletion.
    """
    if item_id:
        cache.delete(make_cache_key(prefix, "item", item_id))
    # Clear list caches by deleting common list key
    cache.delete(make_cache_key(prefix, "list"))
    cache.delete(make_cache_key(prefix, "list", include_inactive=False))
    cache.delete(make_cache_key(prefix, "list", include_inactive=True))


class CacheKeyPrefixes:
    """Centralized cache key prefixes for consistency."""
    CATEGORIES = "categories"
    PRODUCTS = "products"
    BRANDS = "brands"
    WAREHOUSES = "warehouses"
    SUPPLIERS = "suppliers"
    CUSTOMERS = "customers"
    STOCK = "stock"
