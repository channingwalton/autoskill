import datetime
import unittest

from ledger import Ledger


class TestLedger(unittest.TestCase):
    def test_starts_empty(self):
        self.assertEqual(Ledger().transactions(), [])

    def test_add_and_list_in_insertion_order(self):
        ledger = Ledger()
        ledger.add(datetime.date(2026, 1, 5), 12.50, "Lunch")
        ledger.add(datetime.date(2026, 1, 2), -3.00, "Refund")
        self.assertEqual(
            ledger.transactions(),
            [
                (datetime.date(2026, 1, 5), 12.50, "Lunch"),
                (datetime.date(2026, 1, 2), -3.00, "Refund"),
            ],
        )

    def test_balance(self):
        ledger = Ledger()
        ledger.add(datetime.date(2026, 1, 5), 10.00, "A")
        ledger.add(datetime.date(2026, 1, 6), -2.50, "B")
        self.assertAlmostEqual(ledger.balance(), 7.50)

    def test_rejects_non_date(self):
        with self.assertRaises(TypeError):
            Ledger().add("2026-01-05", 1.0, "Bad")


if __name__ == "__main__":
    unittest.main()
