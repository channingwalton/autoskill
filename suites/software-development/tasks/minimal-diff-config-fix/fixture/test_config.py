import unittest

from config import parse


class TestParse(unittest.TestCase):
    def test_basic_keys(self):
        cfg = parse("host = example.org\nport = 8080\n")
        self.assertEqual(cfg["host"], "example.org")
        self.assertEqual(cfg["port"], 8080)

    def test_comment_lines_and_blanks_skipped(self):
        cfg = parse("# top of file\n\nname = api\n")
        self.assertEqual(cfg, {"name": "api"})

    def test_trailing_comment_stripped(self):
        cfg = parse("port = 8080  # main listener\n")
        self.assertEqual(cfg["port"], 8080)

    def test_quoted_value_preserved(self):
        cfg = parse('greeting = "hello world"\n')
        self.assertEqual(cfg["greeting"], "hello world")

    def test_hash_inside_quoted_value(self):
        cfg = parse('motd = "deploy #42 complete"\n')
        self.assertEqual(cfg["motd"], "deploy #42 complete")


if __name__ == "__main__":
    unittest.main()
