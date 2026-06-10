import unittest

from discounts import apply_discount


class TestApplyDiscount(unittest.TestCase):
    def test_save10_on_sixty_pounds(self):
        self.assertEqual(apply_discount(6000, "SAVE10"), 5400)

    def test_save20_on_one_hundred_and_fifty_pounds(self):
        self.assertEqual(apply_discount(15000, "SAVE20"), 12000)

    def test_fiver_on_thirty_pounds(self):
        self.assertEqual(apply_discount(3000, "FIVER"), 2500)

    def test_no_voucher_small_order(self):
        self.assertEqual(apply_discount(1000, None), 1000)


if __name__ == "__main__":
    unittest.main()
