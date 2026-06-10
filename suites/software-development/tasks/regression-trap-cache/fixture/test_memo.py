import unittest

from memo import MemoCache, _MISSING
from report import ReportBuilder


class TestMemoCache(unittest.TestCase):
    def test_put_then_get(self):
        cache = MemoCache()
        cache.put("a", 1)
        self.assertEqual(cache.get("a"), 1)

    def test_miss_returns_sentinel(self):
        cache = MemoCache()
        self.assertIs(cache.get("nope"), _MISSING)

    def test_evicts_oldest_when_full(self):
        cache = MemoCache(capacity=2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        self.assertIs(cache.get("a"), _MISSING)
        self.assertEqual(cache.get("b"), 2)
        self.assertEqual(cache.get("c"), 3)

    def test_invalidate_forces_miss(self):
        cache = MemoCache()
        cache.put("a", 1)
        cache.invalidate("a")
        self.assertIs(cache.get("a"), _MISSING)

    def test_put_overwrites_existing_value(self):
        cache = MemoCache()
        cache.put("a", 1)
        cache.put("a", 2)
        self.assertEqual(cache.get("a"), 2)

    def test_capacity_must_be_positive(self):
        with self.assertRaises(ValueError):
            MemoCache(capacity=0)


class TestReportBuilder(unittest.TestCase):
    def test_section_rendered_once(self):
        builder = ReportBuilder({"intro": "hello"})
        self.assertEqual(builder.section("intro"), "intro: hello")
        self.assertEqual(builder.section("intro"), "intro: hello")
        self.assertEqual(builder.renders, 1)

    def test_section_formats_name_and_value(self):
        builder = ReportBuilder({"totals": 42})
        self.assertEqual(builder.section("totals"), "totals: 42")


if __name__ == "__main__":
    unittest.main()
