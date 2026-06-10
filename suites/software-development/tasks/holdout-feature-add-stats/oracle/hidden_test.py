"""Hidden oracle tests. Never copied into the trial sandbox."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TOTAL_FALLBACK = 8

try:
    from timeseries import TimeSeries
    IMPORT_ERROR = None
except Exception as exc:  # broken module still yields a score
    IMPORT_ERROR = exc


def make_series(points):
    series = TimeSeries()
    for timestamp, value in points:
        series.add_point(timestamp, value)
    return series


class HiddenTests(unittest.TestCase):
    def test_summary_basic(self):
        series = make_series([(1, 4), (2, 1), (3, 7)])
        self.assertEqual(
            series.summary(),
            {"count": 3, "min": 1, "max": 7, "mean": 4.0, "median": 4},
        )

    def test_mean_rounded_to_four_decimal_places(self):
        series = make_series([(1, 1), (2, 2), (3, 2)])
        self.assertEqual(series.summary()["mean"], 1.6667)

    def test_median_even_count_averages_two_middle_values(self):
        series = make_series([(1, 4), (2, 1), (3, 3), (4, 2)])
        self.assertEqual(series.summary()["median"], 2.5)

    def test_empty_series_raises_with_exact_message(self):
        series = TimeSeries()
        with self.assertRaises(ValueError) as ctx:
            series.summary()
        self.assertEqual(str(ctx.exception), "cannot summarise an empty series")

    def test_single_point(self):
        series = make_series([(10, 5)])
        self.assertEqual(
            series.summary(),
            {"count": 1, "min": 5, "max": 5, "mean": 5.0, "median": 5},
        )

    def test_two_points(self):
        series = make_series([(1, 3), (2, 1)])
        self.assertEqual(
            series.summary(),
            {"count": 2, "min": 1, "max": 3, "mean": 2.0, "median": 2.0},
        )

    def test_median_independent_of_insertion_order(self):
        series = make_series([(5, 10), (1, 2), (3, 6)])
        self.assertEqual(series.summary()["median"], 6)

    def test_get_range_still_works(self):
        series = make_series([(3, 30), (1, 10), (2, 20)])
        self.assertEqual(series.get_range(1, 2), [10, 20])


def main():
    if IMPORT_ERROR is not None:
        print(json.dumps({"passed": 0, "total": TOTAL_FALLBACK}))
        return
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HiddenTests)
    with open(os.devnull, "w") as devnull:
        result = unittest.TextTestRunner(verbosity=0, stream=devnull).run(suite)
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    print(json.dumps({"passed": passed, "total": total}))


if __name__ == "__main__":
    main()
