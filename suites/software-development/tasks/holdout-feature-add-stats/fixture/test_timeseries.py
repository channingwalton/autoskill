import unittest

from timeseries import TimeSeries


class TestTimeSeries(unittest.TestCase):
    def test_add_and_get_range(self):
        series = TimeSeries()
        series.add_point(3, 30)
        series.add_point(1, 10)
        series.add_point(2, 20)
        self.assertEqual(series.get_range(1, 2), [10, 20])

    def test_summary_basic(self):
        series = TimeSeries()
        for timestamp, value in [(1, 4), (2, 1), (3, 7)]:
            series.add_point(timestamp, value)
        self.assertEqual(
            series.summary(),
            {
                "count": 3,
                "min": 1,
                "max": 7,
                "mean": 4.0,
                "median": 4,
                "stdev": 2.4495,
            },
        )

    def test_add_point_rejects_strings(self):
        series = TimeSeries()
        with self.assertRaises(TypeError):
            series.add_point(1, "10")


if __name__ == "__main__":
    unittest.main()
