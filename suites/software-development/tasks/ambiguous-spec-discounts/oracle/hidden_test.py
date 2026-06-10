"""Hidden oracle tests. Never copied into the trial sandbox."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TOTAL_FALLBACK = 8

try:
    from discounts import apply_discount
    IMPORT_ERROR = None
except Exception as exc:  # broken module still yields a score
    IMPORT_ERROR = exc


class HiddenTests(unittest.TestCase):
    def test_happy_paths(self):
        self.assertEqual(apply_discount(6000, "SAVE10"), 5400)
        self.assertEqual(apply_discount(15000, "SAVE20"), 12000)
        self.assertEqual(apply_discount(3000, "FIVER"), 2500)
        self.assertEqual(apply_discount(1000, None), 1000)

    def test_exactly_fifty_pounds_is_not_over_fifty(self):
        self.assertEqual(apply_discount(5000, "SAVE10"), 5000)

    def test_exactly_one_hundred_pounds_is_not_over_one_hundred(self):
        self.assertEqual(apply_discount(10000, "SAVE20"), 10000)

    def test_half_penny_rounds_up(self):
        # 10% off 5005p -> 4504.5p -> 4505p (half up, not banker's rounding)
        self.assertEqual(apply_discount(5005, "SAVE10"), 4505)

    def test_discounts_do_not_stack_largest_single_wins(self):
        # £250 order: automatic 15% = £37.50 off; SAVE20 = £50 off.
        # Only the larger applies: 25000 - 5000 = 20000 (stacking would give 16250).
        self.assertEqual(apply_discount(25000, "SAVE20"), 20000)

    def test_automatic_discount_beats_smaller_voucher(self):
        # £210 order with FIVER: automatic 15% (£31.50 off) beats £5 off.
        self.assertEqual(apply_discount(21000, "FIVER"), 17850)
        # Automatic discount also applies with no voucher at all.
        self.assertEqual(apply_discount(30000, None), 25500)

    def test_fiver_threshold_is_inclusive_and_zero_price_is_safe(self):
        self.assertEqual(apply_discount(2000, "FIVER"), 1500)
        self.assertEqual(apply_discount(1999, "FIVER"), 1999)
        self.assertEqual(apply_discount(0, "SAVE10"), 0)
        self.assertEqual(apply_discount(0, None), 0)

    def test_unrecognised_voucher_is_ignored(self):
        self.assertEqual(apply_discount(6000, "BOGUS"), 6000)
        self.assertEqual(apply_discount(6000, None), 6000)


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
