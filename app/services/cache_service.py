import time
_cache = {}
_expiration_seconds = 1800

def set_expiration(seconds):
    global _expiration_seconds
    _expiration_seconds = seconds

def get_from_cache(key):
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry['timestamp'] < _expiration_seconds:
            return entry['data']
        else:
            del _cache[key]
    return None

def set_in_cache(key, value):
    _cache[key] = {
        'timestamp': time.time(),
        'data': value
    }
        
def clear_cache():
    global _cache
    _cache = {}
