"""Hidden oracle tests. Never copied into the trial sandbox."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TOTAL_FALLBACK = 8

try:
    from memo import MemoCache, _MISSING
    from report import ReportBuilder
    IMPORT_ERROR = None
except Exception as exc:  # broken module still yields a score
    IMPORT_ERROR = exc


class HiddenTests(unittest.TestCase):
    # ----- the reported bug --------------------------------------------
    def test_invalidate_forces_miss(self):
        cache = MemoCache()
        cache.put("a", 1)
        cache.invalidate("a")
        self.assertIs(cache.get("a"), _MISSING)

    def test_invalidate_then_reput(self):
        cache = MemoCache()
        cache.put("a", 1)
        cache.invalidate("a")
        cache.put("a", 2)
        self.assertEqual(cache.get("a"), 2)

    def test_invalidate_unknown_key_is_noop(self):
        cache = MemoCache()
        cache.invalidate("ghost")
        self.assertIs(cache.get("ghost"), _MISSING)

    # ----- the adjacent behaviour a careless fix breaks ------------------
    def test_none_is_a_valid_cached_value(self):
        cache = MemoCache()
        cache.put("x", None)
        self.assertIsNone(cache.get("x"))
        self.assertIsNot(cache.get("x"), _MISSING)

    def test_empty_section_rendered_only_once(self):
        builder = ReportBuilder({"notes": None})
        self.assertIsNone(builder.section("notes"))
        self.assertIsNone(builder.section("notes"))
        self.assertEqual(builder.renders, 1)

    def test_refresh_forces_exactly_one_rerender(self):
        builder = ReportBuilder({"intro": "hello"})
        self.assertEqual(builder.section("intro"), "intro: hello")
        self.assertEqual(builder.renders, 1)
        builder.refresh("intro")
        self.assertEqual(builder.section("intro"), "intro: hello")
        self.assertEqual(builder.renders, 2)
        self.assertEqual(builder.section("intro"), "intro: hello")
        self.assertEqual(builder.renders, 2)

    # ----- regression guards ---------------------------------------------
    def test_eviction_is_still_fifo(self):
        builder = ReportBuilder({"a": 1, "b": 2, "c": 3}, capacity=2)
        builder.section("a")
        builder.section("b")
        builder.section("c")  # evicts a
        builder.section("a")  # re-rendered
        self.assertEqual(builder.renders, 4)

    def test_invalidate_frees_a_slot(self):
        cache = MemoCache(capacity=2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.invalidate("a")
        cache.put("c", 3)
        self.assertEqual(cache.get("b"), 2)
        self.assertEqual(cache.get("c"), 3)


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
