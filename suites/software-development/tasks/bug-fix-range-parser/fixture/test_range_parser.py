import unittest

from range_parser import parse_range


class TestParseRange(unittest.TestCase):
    def test_single_page(self):
        self.assertEqual(parse_range("3"), [3])

    def test_simple_range_is_inclusive(self):
        self.assertEqual(parse_range("1-3"), [1, 2, 3])

    def test_range_and_single(self):
        self.assertEqual(parse_range("1-3,7"), [1, 2, 3, 7])


if __name__ == "__main__":
    unittest.main()
