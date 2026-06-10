"""Hidden oracle tests. Never copied into the trial sandbox."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TOTAL_FALLBACK = 11

try:
    from range_parser import parse_range
    IMPORT_ERROR = None
except Exception as exc:  # broken module still yields a score
    IMPORT_ERROR = exc


class HiddenTests(unittest.TestCase):
    def test_single_page(self):
        self.assertEqual(parse_range("3"), [3])

    def test_range_inclusive_both_ends(self):
        self.assertEqual(parse_range("1-5"), [1, 2, 3, 4, 5])

    def test_mixed_parts(self):
        self.assertEqual(parse_range("1-3,7,9-10"), [1, 2, 3, 7, 9, 10])

    def test_whitespace_tolerated_anywhere(self):
        self.assertEqual(parse_range(" 1 - 3 , 7 "), [1, 2, 3, 7])
        self.assertEqual(parse_range("1-3, 7"), [1, 2, 3, 7])
        self.assertEqual(parse_range("\t2 - 4\t"), [2, 3, 4])

    def test_empty_parts_ignored(self):
        self.assertEqual(parse_range("1,,3"), [1, 3])
        self.assertEqual(parse_range("1-3,"), [1, 2, 3])
        self.assertEqual(parse_range(",2-4,"), [2, 3, 4])

    def test_empty_spec_gives_empty_list(self):
        self.assertEqual(parse_range(""), [])
        self.assertEqual(parse_range("  "), [])

    def test_duplicates_collapse(self):
        self.assertEqual(parse_range("1-3,2,3"), [1, 2, 3])

    def test_single_element_range(self):
        self.assertEqual(parse_range("4-4"), [4])

    def test_zero_is_a_valid_page(self):
        self.assertEqual(parse_range("0-2"), [0, 1, 2])
        self.assertEqual(parse_range("0"), [0])

    def test_reversed_range_raises_naming_the_part(self):
        with self.assertRaises(ValueError) as ctx:
            parse_range("5-3")
        self.assertIn("5-3", str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            parse_range("1,9-7")
        self.assertIn("9-7", str(ctx.exception))

    def test_negative_numbers_raise_value_error(self):
        with self.assertRaises(ValueError):
            parse_range("-3")
        with self.assertRaises(ValueError):
            parse_range("1,-2")
        with self.assertRaises(ValueError):
            parse_range("1--3")


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
