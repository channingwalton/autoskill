"""Hidden oracle tests. Never copied into the trial sandbox."""

import csv
import datetime
import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TOTAL_FALLBACK = 8

try:
    from ledger import Ledger
    IMPORT_ERROR = None
except Exception as exc:  # broken module still yields a score
    IMPORT_ERROR = exc


def parse(output):
    return list(csv.reader(io.StringIO(output)))


class HiddenTests(unittest.TestCase):
    def test_existing_behaviour_unchanged(self):
        ledger = Ledger()
        ledger.add(datetime.date(2026, 1, 5), 10.00, "A")
        ledger.add(datetime.date(2026, 1, 6), -2.50, "B")
        self.assertEqual(
            ledger.transactions(),
            [(datetime.date(2026, 1, 5), 10.0, "A"), (datetime.date(2026, 1, 6), -2.5, "B")],
        )
        self.assertAlmostEqual(ledger.balance(), 7.50)
        with self.assertRaises(TypeError):
            ledger.add("2026-01-05", 1.0, "Bad")

    def test_header_row(self):
        rows = parse(Ledger().to_csv())
        self.assertEqual(rows[0], ["date", "amount", "description"])

    def test_empty_ledger_is_header_only(self):
        rows = parse(Ledger().to_csv())
        self.assertEqual(rows, [["date", "amount", "description"]])

    def test_simple_row_iso_date(self):
        ledger = Ledger()
        ledger.add(datetime.date(2026, 3, 7), 19.99, "Books")
        rows = parse(ledger.to_csv())
        self.assertEqual(rows[1], ["2026-03-07", "19.99", "Books"])

    def test_amounts_have_two_decimal_places(self):
        ledger = Ledger()
        ledger.add(datetime.date(2026, 1, 1), 5, "Whole")
        ledger.add(datetime.date(2026, 1, 2), 3.5, "Tenths")
        ledger.add(datetime.date(2026, 1, 3), -12.3, "Negative")
        rows = parse(ledger.to_csv())
        self.assertEqual([row[1] for row in rows[1:]], ["5.00", "3.50", "-12.30"])

    def test_comma_in_description_round_trips(self):
        ledger = Ledger()
        ledger.add(datetime.date(2026, 2, 1), 4.20, "Milk, eggs, and bread")
        rows = parse(ledger.to_csv())
        self.assertEqual(rows[1][2], "Milk, eggs, and bread")
        self.assertEqual(len(rows[1]), 3)

    def test_quotes_and_newlines_round_trip(self):
        ledger = Ledger()
        ledger.add(datetime.date(2026, 2, 2), 1.00, 'He said "hello"')
        ledger.add(datetime.date(2026, 2, 3), 2.00, "Line one\nLine two")
        rows = parse(ledger.to_csv())
        self.assertEqual(rows[1][2], 'He said "hello"')
        self.assertEqual(rows[2][2], "Line one\nLine two")

    def test_rows_in_insertion_order(self):
        ledger = Ledger()
        ledger.add(datetime.date(2026, 5, 9), 1.00, "Later date first")
        ledger.add(datetime.date(2026, 1, 1), 2.00, "Earlier date second")
        rows = parse(ledger.to_csv())
        self.assertEqual([row[0] for row in rows[1:]], ["2026-05-09", "2026-01-01"])


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
