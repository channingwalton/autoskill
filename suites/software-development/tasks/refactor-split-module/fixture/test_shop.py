import unittest

import shop


class TestShop(unittest.TestCase):
    def test_unit_price(self):
        self.assertEqual(shop.unit_price("apple"), 60)

    def test_unknown_item(self):
        with self.assertRaises(KeyError):
            shop.unit_price("caviar")

    def test_bulk_discount_applies_at_ten(self):
        self.assertEqual(shop.line_price("banana", 9), 225)
        self.assertEqual(shop.line_price("banana", 10), 225)

    def test_add_vat(self):
        self.assertEqual(shop.add_vat(250), 300)

    def test_basket_accumulates_and_totals(self):
        basket = shop.Basket()
        basket.add("apple", 2)
        basket.add("milk")
        basket.add("apple")
        self.assertEqual(basket.quantity("apple"), 3)
        self.assertEqual(basket.subtotal(), 3 * 60 + 130)

    def test_receipt(self):
        basket = shop.Basket()
        basket.add("apple", 2)
        basket.add("milk")
        receipt = shop.format_receipt(basket)
        self.assertTrue(receipt.startswith("RECEIPT"))
        self.assertIn("SUBTOTAL £2.50", receipt)
        self.assertIn("TOTAL    £3.00", receipt)


if __name__ == "__main__":
    unittest.main()
