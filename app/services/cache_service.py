import time

# Global cache dictionary
_cache = {}
_expiration_seconds = 1800

def set_expiration(seconds):
    """Set the cache expiration time."""
    global _expiration_seconds
    _expiration_seconds = seconds

def get_from_cache(key):
    """
    Retrieve a value from the cache if it exists and hasn't expired.
    """
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry['timestamp'] < _expiration_seconds:
            return entry['data']
        else:
            # Expired
            del _cache[key]
    return None

def set_in_cache(key, value):
    """
    Store a value in the cache with the current timestamp.
    """
    _cache[key] = {
        'timestamp': time.time(),
        'data': value
    }
        
def clear_cache():
    """Clear the entire cache."""
    global _cache
    _cache = {}
