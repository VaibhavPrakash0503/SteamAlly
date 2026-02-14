class SteamCache:
    def __init__(self):
        self._cache = {}

    def set_cache(self, key, value):
        self._cache[key] = value

    def get_cache(self, key, default=None):
        return self._cache.get(key, default)

    def has_key(self, key):
        return key in self._cache

    def delete_cache(self, key):
        if key in self._cache:
            del self._cache[key]

    def clear_cache(self):
        self._cache.clear()

    def get_keys(self):
        return list(self._cache.keys())
