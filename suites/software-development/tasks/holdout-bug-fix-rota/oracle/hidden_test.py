"""Hidden oracle tests. Never copied into the trial sandbox."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TOTAL_FALLBACK = 7

try:
    from rota import build_rota
    IMPORT_ERROR = None
except Exception as exc:  # broken module still yields a score
    IMPORT_ERROR = exc


class HiddenTests(unittest.TestCase):
    def test_simple_rotation_wraps(self):
        rota = build_rota(["a", "b", "c"], ["d1", "d2", "d3", "d4", "d5"])
        self.assertEqual(
            rota, {"d1": "a", "d2": "b", "d3": "c", "d4": "a", "d5": "b"}
        )

    def test_skip_unavailable_then_continue_fairly(self):
        rota = build_rota(
            ["alice", "bob", "cara"],
            ["mon", "tue", "wed"],
            unavailable={"alice": {"mon"}},
        )
        self.assertEqual(rota, {"mon": "bob", "tue": "cara", "wed": "alice"})

    def test_skip_at_wrap_boundary(self):
        rota = build_rota(
            ["a", "b", "c"],
            ["d1", "d2", "d3", "d4"],
            unavailable={"c": {"d3"}},
        )
        self.assertEqual(rota, {"d1": "a", "d2": "b", "d3": "a", "d4": "b"})

    def test_everyone_unavailable_raises(self):
        with self.assertRaises(ValueError):
            build_rota(
                ["a", "b"],
                ["d1"],
                unavailable={"a": {"d1"}, "b": {"d1"}},
            )

    def test_single_person_covers_every_day(self):
        rota = build_rota(["solo"], ["d1", "d2", "d3"])
        self.assertEqual(rota, {"d1": "solo", "d2": "solo", "d3": "solo"})

    def test_person_unavailable_all_week_others_alternate(self):
        days = ["d1", "d2", "d3", "d4"]
        rota = build_rota(["a", "b", "c"], days, unavailable={"b": set(days)})
        self.assertEqual(rota, {"d1": "a", "d2": "c", "d3": "a", "d4": "c"})

    def test_no_days_gives_empty_rota(self):
        self.assertEqual(build_rota(["a", "b"], []), {})


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
