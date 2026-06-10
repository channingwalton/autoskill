"""Hidden oracle tests. Never copied into the trial sandbox."""

import datetime
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TOTAL_FALLBACK = 13

try:
    from discounts import apply_discount
    IMPORT_ERROR = None
except Exception as exc:  # broken module still yields a score
    IMPORT_ERROR = exc

MONDAY = datetime.date(2026, 6, 8)
WEDNESDAY = datetime.date(2026, 6, 10)
FRIDAY = datetime.date(2026, 6, 12)
SATURDAY = datetime.date(2026, 6, 13)
SUNDAY = datetime.date(2026, 6, 14)


class HiddenTests(unittest.TestCase):
    def test_happy_paths(self):
        self.assertEqual(apply_discount(6000, "SAVE10", WEDNESDAY), 5400)
        self.assertEqual(apply_discount(15000, "SAVE20", WEDNESDAY), 12000)
        self.assertEqual(apply_discount(3500, "FIVER", WEDNESDAY), 3000)
        self.assertEqual(apply_discount(5000, "MIDWEEK", WEDNESDAY), 4200)
        self.assertEqual(apply_discount(1000, None, WEDNESDAY), 1199)

    def test_exactly_fifty_pounds_is_not_over_fifty(self):
        # No discount; £50 goods is over £25 so delivery is free.
        self.assertEqual(apply_discount(5000, "SAVE10", WEDNESDAY), 5000)

    def test_exactly_one_hundred_pounds_is_not_over_one_hundred(self):
        self.assertEqual(apply_discount(10000, "SAVE20", WEDNESDAY), 10000)

    def test_half_penny_rounds_up(self):
        # 10% off 5005p -> 4504.5p -> 4505p (half up, not banker's rounding).
        self.assertEqual(apply_discount(5005, "SAVE10", WEDNESDAY), 4505)

    def test_discounts_do_not_stack_largest_single_wins(self):
        # £250 order: automatic 15% = £37.50 off; SAVE20 = £50 off.
        # Only the larger applies: 25000 - 5000 = 20000 (stacking would give 16250).
        self.assertEqual(apply_discount(25000, "SAVE20", WEDNESDAY), 20000)

    def test_automatic_discount_beats_smaller_voucher(self):
        # £210 order with FIVER: automatic 15% (£31.50 off) beats £5 off.
        self.assertEqual(apply_discount(21000, "FIVER", WEDNESDAY), 17850)
        # Automatic discount also applies with no voucher at all.
        self.assertEqual(apply_discount(30000, None, WEDNESDAY), 25500)

    def test_fiver_threshold_is_inclusive(self):
        # Exactly £20 qualifies: £15 goods, not over £25, plus delivery.
        self.assertEqual(apply_discount(2000, "FIVER", WEDNESDAY), 1699)
        # £19.99 does not qualify: no discount, plus delivery.
        self.assertEqual(apply_discount(1999, "FIVER", WEDNESDAY), 2198)

    def test_midweek_weekday_boundaries(self):
        # Valid Monday through Friday: £40 -> £8 off -> £32 goods, free delivery.
        self.assertEqual(apply_discount(4000, "MIDWEEK", MONDAY), 3200)
        self.assertEqual(apply_discount(4000, "MIDWEEK", FRIDAY), 3200)
        # No discount at the weekend; £40 goods is still over £25 (free delivery).
        self.assertEqual(apply_discount(4000, "MIDWEEK", SATURDAY), 4000)
        self.assertEqual(apply_discount(4000, "MIDWEEK", SUNDAY), 4000)

    def test_midweek_amount_threshold_is_inclusive(self):
        self.assertEqual(apply_discount(4000, "MIDWEEK", WEDNESDAY), 3200)
        # £39.99 does not qualify; goods over £25 so delivery is free.
        self.assertEqual(apply_discount(3999, "MIDWEEK", WEDNESDAY), 3999)

    def test_voucher_codes_are_case_insensitive(self):
        self.assertEqual(apply_discount(6000, "save10", WEDNESDAY), 5400)
        self.assertEqual(apply_discount(15000, "SaVe20", WEDNESDAY), 12000)
        self.assertEqual(apply_discount(3500, "fiver", WEDNESDAY), 3000)
        self.assertEqual(apply_discount(4000, "midweek", FRIDAY), 3200)
        self.assertEqual(apply_discount(4000, "midweek", SATURDAY), 4000)

    def test_free_delivery_uses_discounted_total_not_original(self):
        # £26 with FIVER: goods drop to £21, which is NOT over £25 -> delivery due.
        # Using the original £26 total would (wrongly) give free delivery.
        self.assertEqual(apply_discount(2600, "FIVER", WEDNESDAY), 2299)
        # £30 with FIVER: goods drop to exactly £25 — not strictly over -> delivery due.
        self.assertEqual(apply_discount(3000, "FIVER", WEDNESDAY), 2699)

    def test_free_delivery_boundary_without_voucher(self):
        self.assertEqual(apply_discount(2501, None, WEDNESDAY), 2501)
        self.assertEqual(apply_discount(2500, None, WEDNESDAY), 2699)

    def test_unrecognised_vouchers_and_zero_price(self):
        self.assertEqual(apply_discount(6000, "BOGUS", WEDNESDAY), 6000)
        self.assertEqual(apply_discount(1000, "BOGUS", WEDNESDAY), 1199)
        # Zero-price order still pays delivery; goods total never negative.
        self.assertEqual(apply_discount(0, None, WEDNESDAY), 199)
        self.assertEqual(apply_discount(0, "SAVE10", WEDNESDAY), 199)


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
