"""A minimal in-memory time series."""


class TimeSeries:
    """Stores (timestamp, value) points and answers range queries."""

    def __init__(self):
        self._points = []

    def add_point(self, timestamp, value):
        """Record a value at the given timestamp."""
        self._points.append((timestamp, value))

    def get_range(self, start, end):
        """Return values whose timestamp t satisfies start <= t <= end.

        Values come back in timestamp order regardless of insertion order.
        """
        selected = [(t, v) for t, v in self._points if start <= t <= end]
        return [v for t, v in sorted(selected)]
