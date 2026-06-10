"""Hidden oracle tests. Never copied into the trial sandbox."""

import importlib
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

TOTAL_FALLBACK = 13

try:
    import shop
    IMPORT_ERROR = None
except Exception as exc:  # broken module still yields a score
    IMPORT_ERROR = exc


def import_side_effects(module):
    """Import `module` in a fresh interpreter; return the loaded local modules."""
    code = (
        "import sys, json\n"
        "import {0}\n"
        "names = ('pricing', 'basket', 'report', 'shop')\n"
        "print(json.dumps([n for n in names if n in sys.modules]))\n"
    ).format(module)
    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=HERE,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return set(json.loads(proc.stdout))


class HiddenTests(unittest.TestCase):
    def test_pricing_behaviour_via_shop(self):
        self.assertEqual(shop.unit_price("apple"), 60)
        self.assertEqual(shop.unit_price("cheese"), 350)
        with self.assertRaises(KeyError):
            shop.unit_price("caviar")

    def test_bulk_discount_boundary(self):
        self.assertEqual(shop.line_price("banana", 9), 225)
        self.assertEqual(shop.line_price("banana", 10), 225)
        self.assertEqual(shop.line_price("apple", 0), 0)
        with self.assertRaises(ValueError):
            shop.line_price("apple", -1)

    def test_vat(self):
        self.assertEqual(shop.add_vat(250), 300)
        self.assertEqual(shop.add_vat(0), 0)

    def test_basket_behaviour(self):
        basket = shop.Basket()
        basket.add("apple", 2)
        basket.add("milk")
        basket.add("apple")
        self.assertEqual(basket.quantity("apple"), 3)
        self.assertEqual(basket.subtotal(), 3 * 60 + 130)
        basket.remove("milk")
        self.assertEqual(basket.quantity("milk"), 0)
        self.assertEqual(basket.subtotal(), 3 * 60)
        self.assertEqual(basket.total_with_vat(), shop.add_vat(3 * 60))

    def test_receipt_content(self):
        basket = shop.Basket()
        basket.add("apple", 2)
        basket.add("milk")
        receipt = shop.format_receipt(basket)
        self.assertTrue(receipt.startswith("RECEIPT"))
        self.assertIn("apple", receipt)
        self.assertIn("milk", receipt)
        self.assertIn("SUBTOTAL £2.50", receipt)
        self.assertIn("TOTAL    £3.00", receipt)
        self.assertEqual(
            shop.format_line("apple", 2, 120),
            f"{2:>3} x {'apple':<12}{shop.format_pence(120):>8}",
        )

    def test_split_modules_exist_with_expected_api(self):
        pricing = importlib.import_module("pricing")
        for name in ("PRICES", "unit_price", "line_price", "add_vat"):
            self.assertTrue(hasattr(pricing, name), f"pricing.{name} missing")
        basket_mod = importlib.import_module("basket")
        self.assertTrue(hasattr(basket_mod, "Basket"), "basket.Basket missing")
        report = importlib.import_module("report")
        for name in ("format_pence", "format_line", "format_receipt"):
            self.assertTrue(hasattr(report, name), f"report.{name} missing")

    def test_split_modules_behave(self):
        pricing = importlib.import_module("pricing")
        basket_mod = importlib.import_module("basket")
        report = importlib.import_module("report")
        self.assertEqual(pricing.unit_price("bread"), 110)
        basket = basket_mod.Basket()
        basket.add("bread")
        self.assertEqual(basket.subtotal(), 110)
        self.assertIn("bread", report.format_receipt(basket))

    def test_shim_re_exports_same_objects(self):
        pricing = importlib.import_module("pricing")
        basket_mod = importlib.import_module("basket")
        report = importlib.import_module("report")
        self.assertIs(shop.PRICES, pricing.PRICES)
        self.assertIs(shop.unit_price, pricing.unit_price)
        self.assertIs(shop.Basket, basket_mod.Basket)
        self.assertIs(shop.format_pence, report.format_pence)
        self.assertEqual(shop.BULK_THRESHOLD, 10)
        self.assertEqual(shop.VAT_PERCENT, 20)

    def test_audit_module_still_works(self):
        audit = importlib.import_module("audit")
        self.assertEqual(audit.audit_value({"apple": 2, "milk": 1}), 250)
        self.assertEqual(audit.audit_value({"banana": 10}), 225)
        self.assertEqual(audit.insured_value({"apple": 2, "milk": 1}), 300)
        self.assertEqual(audit.full_catalogue_value(), 675)

    def test_audit_report_still_works(self):
        audit = importlib.import_module("audit")
        report = audit.audit_report({"apple": 2})
        self.assertTrue(report.startswith("AUDIT"))
        self.assertIn("apple", report)
        self.assertIn("VALUE   £1.20", report)
        self.assertIn("INSURED £1.44", report)

    def test_importing_pricing_loads_neither_basket_nor_report(self):
        loaded = import_side_effects("pricing")
        self.assertNotIn("basket", loaded)
        self.assertNotIn("report", loaded)

    def test_importing_basket_does_not_load_report(self):
        loaded = import_side_effects("basket")
        self.assertNotIn("report", loaded)

    def test_shop_is_a_thin_shim(self):
        path = os.path.join(HERE, "shop.py")
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        line_count = len(source.splitlines())
        self.assertLessEqual(line_count, 30, f"shop.py has {line_count} lines; expected <= 30")
        for forbidden in ("def ", "class "):
            self.assertNotIn(
                forbidden, source,
                f"shop.py contains a {forbidden.strip()} statement; it must only re-export",
            )


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
