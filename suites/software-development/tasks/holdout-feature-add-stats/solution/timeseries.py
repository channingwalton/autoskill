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

    def summary(self):
        """Return count, min, max, mean (4 dp) and median of all values."""
        if not self._points:
            raise ValueError("cannot summarise an empty series")
        values = sorted(value for _, value in self._points)
        count = len(values)
        middle = count // 2
        if count % 2 == 1:
            median = values[middle]
        else:
            median = (values[middle - 1] + values[middle]) / 2
        return {
            "count": count,
            "min": values[0],
            "max": values[-1],
            "mean": round(sum(values) / count, 4),
            "median": median,
        }
