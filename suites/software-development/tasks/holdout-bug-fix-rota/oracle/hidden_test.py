"""Hidden oracle tests. Never copied into the trial sandbox."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TOTAL_FALLBACK = 14

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

    # --- contract clauses from the docstring -----------------------------

    def test_skip_then_pointer_moves_past_assignee(self):
        # After a skip the pointer continues from after the *assigned*
        # person, not merely one step from where it started.
        rota = build_rota(
            ["a", "b", "c"],
            ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8"],
            unavailable={"a": {"d4", "d5"}},
        )
        self.assertEqual(
            rota,
            {
                "d1": "a", "d2": "b", "d3": "c", "d4": "b",
                "d5": "c", "d6": "a", "d7": "b", "d8": "c",
            },
        )

    def test_multi_week_fairness_over_full_cycles(self):
        days = ["d%02d" % i for i in range(1, 13)]
        rota = build_rota(["a", "b", "c"], days)
        counts = {}
        for person in rota.values():
            counts[person] = counts.get(person, 0) + 1
        self.assertEqual(counts, {"a": 4, "b": 4, "c": 4})

    def test_inputs_not_mutated(self):
        people = ["a", "b", "c"]
        unavailable = {"a": {"d1"}, "zed": {"d2"}}
        build_rota(people, ["d1", "d2", "d3"], unavailable)
        self.assertEqual(people, ["a", "b", "c"])
        self.assertEqual(unavailable, {"a": {"d1"}, "zed": {"d2"}})

    def test_repeated_calls_return_same_rota(self):
        args = (["a", "b", "c"], ["d1", "d2", "d3", "d4"], {"b": {"d2"}})
        first = build_rota(*args)
        second = build_rota(*args)
        self.assertEqual(first, second)

    def test_unknown_name_in_unavailable_is_ignored(self):
        rota = build_rota(
            ["a", "b"], ["d1", "d2"], unavailable={"zed": {"d1", "d2"}}
        )
        self.assertEqual(rota, {"d1": "a", "d2": "b"})

    def test_error_message_names_the_blocked_day(self):
        with self.assertRaises(ValueError) as ctx:
            build_rota(
                ["a", "b"],
                ["d1", "d2", "d3"],
                unavailable={"a": {"d2"}, "b": {"d2"}},
            )
        self.assertEqual(str(ctx.exception), "no one is available on d2")

    def test_empty_people_with_days_raises(self):
        with self.assertRaises(ValueError) as ctx:
            build_rota([], ["d1"])
        self.assertEqual(str(ctx.exception), "no one is available on d1")


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
