import unittest

from rota import build_rota


class TestBuildRota(unittest.TestCase):
    def test_simple_rotation(self):
        rota = build_rota(["alice", "bob", "cara"], ["mon", "tue", "wed"])
        self.assertEqual(rota, {"mon": "alice", "tue": "bob", "wed": "cara"})

    def test_skips_unavailable_and_stays_fair(self):
        rota = build_rota(
            ["alice", "bob", "cara"],
            ["mon", "tue", "wed"],
            unavailable={"alice": {"mon"}},
        )
        self.assertEqual(rota, {"mon": "bob", "tue": "cara", "wed": "alice"})


if __name__ == "__main__":
    unittest.main()
