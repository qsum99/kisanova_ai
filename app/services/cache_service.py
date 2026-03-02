import time

class CacheService:
    """
    A simple thread-safe, in-memory caching service 
    to prevent unnecessary API calls.
    """
    def __init__(self, expiration_seconds=1800):
        self.cache = {}
        self.expiration_seconds = expiration_seconds

    def get(self, key):
        """
        Retrieve a value from the cache if it exists and hasn't expired.
        """
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.expiration_seconds:
                return entry['data']
            else:
                # Expired
                del self.cache[key]
        return None

    def set(self, key, value):
        """
        Store a value in the cache with the current timestamp.
        """
        self.cache[key] = {
            'timestamp': time.time(),
            'data': value
        }
        
    def clear(self):
        """Clear the entire cache."""
        self.cache = {}

# Singleton instance to be used across the app
weather_cache = CacheService(expiration_seconds=1800)
