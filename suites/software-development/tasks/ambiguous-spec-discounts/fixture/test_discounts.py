import datetime
import unittest

from discounts import apply_discount

WEDNESDAY = datetime.date(2026, 6, 10)


class TestApplyDiscount(unittest.TestCase):
    def test_save10_on_sixty_pounds(self):
        # £60 -> 10% off -> £54 goods; over £25, so delivery is free.
        self.assertEqual(apply_discount(6000, "SAVE10", WEDNESDAY), 5400)

    def test_save20_on_one_hundred_and_fifty_pounds(self):
        self.assertEqual(apply_discount(15000, "SAVE20", WEDNESDAY), 12000)

    def test_fiver_on_thirty_five_pounds(self):
        # £35 -> £5 off -> £30 goods; over £25, so delivery is free.
        self.assertEqual(apply_discount(3500, "FIVER", WEDNESDAY), 3000)

    def test_midweek_on_fifty_pounds_on_a_wednesday(self):
        # £50 -> £8 off -> £42 goods; over £25, so delivery is free.
        self.assertEqual(apply_discount(5000, "MIDWEEK", WEDNESDAY), 4200)

    def test_no_voucher_small_order_pays_delivery(self):
        # £10 goods, no discount; not over £25, so £1.99 delivery is added.
        self.assertEqual(apply_discount(1000, None, WEDNESDAY), 1199)


if __name__ == "__main__":
    unittest.main()
