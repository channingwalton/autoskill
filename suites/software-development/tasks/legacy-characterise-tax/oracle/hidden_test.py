"""Hidden oracle tests. Never copied into the trial sandbox."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TOTAL_FALLBACK = 12

try:
    from tax import compute_tax
    IMPORT_ERROR = None
except Exception as exc:  # broken module still yields a score
    IMPORT_ERROR = exc


class HiddenTests(unittest.TestCase):
    # ----- unchanged behaviour ---------------------------------------
    def test_basic_rate_unchanged(self):
        self.assertAlmostEqual(compute_tax(30000), 3486.0, places=2)

    def test_higher_rate_unchanged(self):
        self.assertAlmostEqual(compute_tax(60000), 11432.0, places=2)

    def test_no_taper_at_exact_threshold(self):
        self.assertAlmostEqual(compute_tax(100000), 27432.0, places=2)

    def test_marriage_transfer_unchanged(self):
        self.assertAlmostEqual(compute_tax(20000, True), 1234.0, places=2)

    def test_marriage_transfer_still_capped(self):
        self.assertAlmostEqual(compute_tax(13000, True), 0.0, places=2)

    # ----- band and cap boundaries (all unchanged behaviour) -----------
    def test_taxable_exactly_at_basic_band_top(self):
        # 50270: allowance 12570, taxable exactly 37700, all at 20%.
        self.assertAlmostEqual(compute_tax(50270), 7540.0, places=2)

    def test_marriage_transfer_at_exact_eligibility_edge(self):
        # 50270 is the last income eligible for the transfer; 50271 is not.
        self.assertAlmostEqual(compute_tax(50270, True), 7288.0, places=2)
        self.assertAlmostEqual(compute_tax(50271, True), 7540.4, places=2)

    def test_marriage_transfer_ignored_in_taper_region(self):
        # Taper recipients are far above 50270, so the flag changes nothing.
        self.assertAlmostEqual(compute_tax(110000, True),
                               compute_tax(110000), places=2)

    # ----- new taper: exact exhaustion boundary -------------------------
    def test_allowance_exhausted_exactly_at_new_boundary(self):
        # 137710: 37710 // 3 == 12570, allowance exactly zero.
        # 137709: 37709 // 3 == 12569, one pound of allowance survives.
        self.assertAlmostEqual(compute_tax(137710), 48808.0, places=2)
        self.assertAlmostEqual(compute_tax(137709), 48807.1, places=2)

    # ----- changed behaviour: taper is now £1 per £3 ------------------
    def test_taper_one_pound_per_three(self):
        # 110000: allowance 12570 - 10000 // 3 = 9237; taxable 100763
        self.assertAlmostEqual(compute_tax(110000), 32765.2, places=2)

    def test_allowance_survives_past_old_cutoff(self):
        # 130000 is past the old 125140 cliff but under the new rate the
        # allowance is 12570 - 30000 // 3 = 2570, not zero.
        self.assertAlmostEqual(compute_tax(130000), 44182.0, places=2)

    def test_allowance_exhausted_under_new_rate(self):
        # 140000: 40000 // 3 = 13333 > 12570, allowance floors at zero.
        self.assertAlmostEqual(compute_tax(140000), 49838.5, places=2)


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
