"""Small FIFO-eviction memo cache.

None is a legitimate cached value (callers cache lookups that can come
back empty), so lookups signal absence with the module-level _MISSING
sentinel, never with None.
"""

_MISSING = object()


class MemoCache:
    def __init__(self, capacity=4):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self._capacity = capacity
        self._data = {}  # insertion order doubles as the eviction queue

    def get(self, key):
        """Return the cached value for key, or _MISSING if absent."""
        if key in self._data:
            return self._data[key]
        return _MISSING

    def put(self, key, value):
        """Cache value under key, evicting the oldest entry when full."""
        if key in self._data:
            self._data[key] = value
            return
        if len(self._data) >= self._capacity:
            oldest = next(iter(self._data))
            del self._data[oldest]
        self._data[key] = value

    def invalidate(self, key):
        """Drop key from the cache so the next lookup misses."""
        self._data.pop(key, None)
