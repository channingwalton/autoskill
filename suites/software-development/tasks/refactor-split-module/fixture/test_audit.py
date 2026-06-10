import unittest

import audit


class TestAudit(unittest.TestCase):
    def test_audit_value(self):
        self.assertEqual(audit.audit_value({"apple": 2, "milk": 1}), 2 * 60 + 130)

    def test_audit_value_applies_bulk_discount(self):
        self.assertEqual(audit.audit_value({"banana": 10}), 225)

    def test_insured_value_includes_vat(self):
        self.assertEqual(audit.insured_value({"apple": 2, "milk": 1}), 300)

    def test_audit_report(self):
        report = audit.audit_report({"apple": 2})
        self.assertTrue(report.startswith("AUDIT"))
        self.assertIn("apple", report)
        self.assertIn("VALUE   £1.20", report)
        self.assertIn("INSURED £1.44", report)

    def test_full_catalogue_value(self):
        self.assertEqual(audit.full_catalogue_value(), 60 + 25 + 130 + 110 + 350)


if __name__ == "__main__":
    unittest.main()
