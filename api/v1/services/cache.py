from functools import wraps

def cache(func):
    """
    A simple cache decorator.
    """
    cache_dict = {}
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache_dict:
            cache_dict[key] = await func(*args, **kwargs)
        return cache_dict[key]
    
    return wrapper