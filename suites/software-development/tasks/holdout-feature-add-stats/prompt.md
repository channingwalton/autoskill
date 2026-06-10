Please add a `summary()` method to the `TimeSeries` class in `timeseries.py`.

Requirements:

- It returns a dict with the keys `count`, `min`, `max`, `mean`, and
  `median`, computed over the values of all points in the series
  (insertion order must not matter).
- Calling it on an empty series raises `ValueError` with the message
  `cannot summarise an empty series`.
- The median is the middle value of the values sorted ascending; for an
  even number of points it is the average of the two middle values.
- The mean is rounded to 4 decimal places.

There is a test in `test_timeseries.py` covering the basics — make sure the
test suite passes when you are done.
