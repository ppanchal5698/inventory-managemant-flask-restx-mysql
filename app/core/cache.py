# Cache utilities for Redis caching (Async)

import pickle
from functools import wraps
from app.extensions import redis_client

class CacheKeyPrefixes:
    """Centralized cache key prefixes for consistency."""
    CATEGORIES = "categories"
    PRODUCTS = "products"
    BRANDS = "brands"
    WAREHOUSES = "warehouses"
    SUPPLIERS = "suppliers"
    CUSTOMERS = "customers"
    STOCK = "stock"
    SALES_ORDERS = "sales_orders"
    PURCHASE_ORDERS = "purchase_orders"

def make_cache_key(prefix, *args, **kwargs):
    """Generate a cache key from prefix and arguments."""
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None)
    return ":".join(key_parts)

def cached(prefix, type_suffix="item", timeout=300):
    """Async decorator to cache results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not redis_client:
                # Fallback if redis not configured
                return await func(*args, **kwargs)

            # Construct key
            # Handle instance methods: args[0] might be self/cls
            # But make_cache_key expects strings.
            # We skip self/cls for key generation usually.
            # Services are static methods mostly in this app?
            # Yes, CategoryService methods are static.
            # So args are actual arguments.

            # Identify if it's "list" or "item" based on usage?
            # Usage: @cached_list(PREFIX) or @cached_item(PREFIX)
            # We can use the type_suffix.

            # For cached_item, args[0] might be ID.
            # For cached_list, args might be filters.

            cache_key = make_cache_key(prefix, type_suffix, *args, **kwargs)

            # Get from cache
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return pickle.loads(cached_data)

            # Call function
            result = await func(*args, **kwargs)

            # Set cache
            if result is not None:
                await redis_client.set(cache_key, pickle.dumps(result), ex=timeout)

            return result
        return wrapper
    return decorator

def cached_list(prefix, timeout=300):
    return cached(prefix, "list", timeout)

def cached_item(prefix, timeout=300):
    return cached(prefix, "item", timeout)

async def invalidate_cache(prefix, item_id=None):
    """
    Invalidate cache entries for a given prefix.
    """
    if not redis_client:
        return

    if item_id:
        await redis_client.delete(make_cache_key(prefix, "item", item_id))

    # Invalidate lists.
    # Since we don't know exact keys (args), we might need to use SCAN or
    # delete known keys.
    # The existing code deleted specific keys: "list", "list:include_inactive=False", etc.
    # We should delete pattern?
    # redis scan_iter

    pattern = f"{prefix}:list*"
    keys = []
    async for key in redis_client.scan_iter(match=pattern):
        keys.append(key)

    if keys:
        await redis_client.delete(*keys)
