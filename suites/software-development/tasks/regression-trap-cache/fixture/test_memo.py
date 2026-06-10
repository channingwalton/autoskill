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


class TestReportBuilder(unittest.TestCase):
    def test_section_rendered_once(self):
        builder = ReportBuilder({"intro": "hello"})
        self.assertEqual(builder.section("intro"), "intro: hello")
        self.assertEqual(builder.section("intro"), "intro: hello")
        self.assertEqual(builder.renders, 1)


if __name__ == "__main__":
    unittest.main()
