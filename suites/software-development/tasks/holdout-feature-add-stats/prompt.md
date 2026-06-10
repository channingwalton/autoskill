Please add a `summary()` method to the `TimeSeries` class in `timeseries.py`,
and tighten `add_point` validation.

Requirements for `summary()`:

- It returns a dict with the keys `count`, `min`, `max`, `mean`, `median`,
  and `stdev`, computed over the values of all points in the series
  (insertion order must not matter).
- Calling it on an empty series raises `ValueError` with the message
  `cannot summarise an empty series`.
- The median is the middle value of the values sorted ascending; for an
  even number of points it is the average of the two middle values.
- `stdev` is the *population* standard deviation (divide by N, not N - 1).
  For a single point it is `0.0`.
- The mean and stdev are each rounded to 4 decimal places.
- `summary()` must not mutate the series: the stored points, including
  their order, are unchanged after the call.

Requirements for `add_point`:

- It raises `TypeError` with the message `value must be int or float` when
  `value` is not an int or a float. `bool` does not count as numeric here
  and must be rejected too.
- It raises `ValueError` with the message `value must not be NaN` when
  `value` is a float NaN. Together these guarantee `summary()` never
  returns NaN.
- A rejected value must not be stored.

Existing behaviour, including `get_range`, must not change. There is a test
in `test_timeseries.py` covering the basics — make sure the test suite
passes when you are done.
