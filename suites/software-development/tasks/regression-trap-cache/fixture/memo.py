"""Small FIFO-eviction memo cache.

None is a legitimate cached value (callers cache lookups that can come
back empty), so lookups signal absence with the module-level _MISSING
sentinel, never with None.

Two further guarantees callers rely on:

* Eviction is strictly first-in-first-out by *first* insertion: lookups
  never refresh an entry's queue position, and overwriting an existing
  key keeps its original position.
* len(cache) is the number of live entries. Invalidating a cached key
  reduces it by one; dashboards report cache occupancy from it.
"""

_MISSING = object()


class MemoCache:
    def __init__(self, capacity=4):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self._capacity = capacity
        self._data = {}  # insertion order doubles as the eviction queue

    def __len__(self):
        """Number of live entries (see module docstring)."""
        return len(self._data)

    def get(self, key):
        """Return the cached value for key, or _MISSING if absent.

        Lookups never change the eviction order (FIFO, not LRU).
        """
        if key in self._data:
            return self._data[key]
        return _MISSING

    def put(self, key, value):
        """Cache value under key, evicting the oldest entry when full.

        Overwriting an existing key keeps its original queue position.
        """
        if key in self._data:
            self._data[key] = value
            return
        if len(self._data) >= self._capacity:
            oldest = next(iter(self._data))
            del self._data[oldest]
        self._data[key] = value

    def invalidate(self, key):
        """Drop key from the cache so the next lookup misses."""
        if key in self._data:
            self._data[key] = None
