"""A minimal in-memory time series."""

import math


class TimeSeries:
    """Stores (timestamp, value) points and answers range queries."""

    def __init__(self):
        self._points = []

    def add_point(self, timestamp, value):
        """Record a value at the given timestamp.

        Raises TypeError for non-numeric values (bool included) and
        ValueError for NaN; rejected values are not stored.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("value must be int or float")
        if isinstance(value, float) and math.isnan(value):
            raise ValueError("value must not be NaN")
        self._points.append((timestamp, value))

    def get_range(self, start, end):
        """Return values whose timestamp t satisfies start <= t <= end.

        Values come back in timestamp order regardless of insertion order.
        """
        selected = [(t, v) for t, v in self._points if start <= t <= end]
        return [v for t, v in sorted(selected)]

    def summary(self):
        """Return count, min, max, mean, median and population stdev.

        Mean and stdev are rounded to 4 decimal places. The stored points
        are left untouched.
        """
        if not self._points:
            raise ValueError("cannot summarise an empty series")
        values = sorted(value for _, value in self._points)
        count = len(values)
        middle = count // 2
        if count % 2 == 1:
            median = values[middle]
        else:
            median = (values[middle - 1] + values[middle]) / 2
        mean = sum(values) / count
        variance = sum((v - mean) ** 2 for v in values) / count
        return {
            "count": count,
            "min": values[0],
            "max": values[-1],
            "mean": round(mean, 4),
            "median": median,
            "stdev": round(math.sqrt(variance), 4),
        }
