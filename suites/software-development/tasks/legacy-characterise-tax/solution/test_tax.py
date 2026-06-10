"""Characterisation tests for tax.py (taper now £1 per £3)."""

import unittest

from tax import compute_tax


class TestComputeTax(unittest.TestCase):
    def test_basic_rate(self):
        self.assertAlmostEqual(compute_tax(30000), 3486.0, places=2)

    def test_higher_rate(self):
        self.assertAlmostEqual(compute_tax(60000), 11432.0, places=2)

    def test_no_taper_at_threshold(self):
        self.assertAlmostEqual(compute_tax(100000), 27432.0, places=2)

    def test_taper_one_per_three(self):
        self.assertAlmostEqual(compute_tax(110000), 32765.2, places=2)

    def test_taper_partial_allowance_remains(self):
        self.assertAlmostEqual(compute_tax(130000), 44182.0, places=2)

    def test_allowance_exhausted(self):
        self.assertAlmostEqual(compute_tax(140000), 49838.5, places=2)

    def test_marriage_transfer(self):
        self.assertAlmostEqual(compute_tax(20000, True), 1234.0, places=2)

    def test_marriage_transfer_capped_at_tax_due(self):
        self.assertAlmostEqual(compute_tax(13000, True), 0.0, places=2)


if __name__ == "__main__":
    unittest.main()
