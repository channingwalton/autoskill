"""Render named report sections, memoising results in a MemoCache.

Sections may legitimately render to None (optional sections with no
data). MemoCache's _MISSING sentinel keeps "cached None" distinct from
"not cached", so an empty section is still only rendered once.
"""

from memo import MemoCache, _MISSING


class ReportBuilder:
    def __init__(self, source, capacity=4):
        self._source = source
        self._cache = MemoCache(capacity)
        self.renders = 0

    def section(self, name):
        """Return the rendered section, rendering at most once per miss."""
        value = self._cache.get(name)
        if value is _MISSING:
            value = self._render(name)
            self._cache.put(name, value)
        return value

    def refresh(self, name):
        """Drop a cached section so the next request re-renders it."""
        self._cache.invalidate(name)

    def cached_sections(self):
        """Number of sections currently held live in the cache.

        The ops dashboard charts this. Sections cached as None count;
        refreshed sections stop counting until they are re-rendered.
        """
        return len(self._cache)

    def _render(self, name):
        self.renders += 1
        raw = self._source.get(name)
        if raw is None:
            return None
        return "%s: %s" % (name, raw)
