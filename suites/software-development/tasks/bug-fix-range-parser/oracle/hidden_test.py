"""Hidden oracle tests. Never copied into the trial sandbox."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TOTAL_FALLBACK = 6

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

    def test_whitespace_tolerated(self):
        self.assertEqual(parse_range(" 1 - 3 , 7 ".replace(" ", "")), [1, 2, 3, 7])
        self.assertEqual(parse_range("1-3, 7"), [1, 2, 3, 7])

    def test_duplicates_collapse(self):
        self.assertEqual(parse_range("1-3,2,3"), [1, 2, 3])

    def test_single_element_range(self):
        self.assertEqual(parse_range("4-4"), [4])


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
