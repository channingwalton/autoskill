"""Hidden oracle tests. Never copied into the trial sandbox."""

import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

TOTAL_FALLBACK = 13

try:
    from config import parse
    IMPORT_ERROR = None
except Exception as exc:  # broken module still yields a score
    IMPORT_ERROR = exc


class HiddenTests(unittest.TestCase):
    # ----- the bug ------------------------------------------------------
    def test_hash_inside_quoted_value(self):
        cfg = parse('motd = "deploy #42 complete"\n')
        self.assertEqual(cfg["motd"], "deploy #42 complete")

    def test_multiple_hashes_in_quotes_with_trailing_comment(self):
        cfg = parse('pattern = "a#b#c"  # delimiter notes\n')
        self.assertEqual(cfg["pattern"], "a#b#c")

    # ----- quoting edges from the docstring spec ---------------------------
    def test_hash_as_first_char_of_quoted_value(self):
        cfg = parse('tag = "#latest"\n')
        self.assertEqual(cfg["tag"], "#latest")

    def test_escaped_quotes_inside_value(self):
        cfg = parse('motd = "she said \\"hi\\" #1"\n')
        self.assertEqual(cfg["motd"], 'she said "hi" #1')

    def test_escaped_quotes_with_trailing_comment(self):
        cfg = parse('note = "a \\"b\\" c"  # comment\n')
        self.assertEqual(cfg["note"], 'a "b" c')

    # ----- blank-line and whitespace handling ------------------------------
    def test_whitespace_only_lines_skipped(self):
        cfg = parse("key = 1\n   \n\t\nother = 2\n")
        self.assertEqual(cfg, {"key": 1, "other": 2})

    def test_indented_comment_and_padded_pairs(self):
        cfg = parse("   # indented comment\n  spaced   =   42  \n")
        self.assertEqual(cfg, {"spaced": 42})

    # ----- regressions ----------------------------------------------------
    def test_trailing_comment_after_quoted_value(self):
        cfg = parse('name = "api"  # service name\n')
        self.assertEqual(cfg["name"], "api")

    def test_trailing_comment_after_unquoted_value(self):
        cfg = parse("port = 8080  # main listener\n")
        self.assertEqual(cfg["port"], 8080)

    def test_quoting_suppresses_coercion(self):
        cfg = parse('flag = "true"\n')
        self.assertEqual(cfg["flag"], "true")
        self.assertIsInstance(cfg["flag"], str)

    def test_coercion_and_skipping_unchanged(self):
        cfg = parse("# header\n\nenabled = true\nratio = 2.5\nlabel = plain\n")
        self.assertIs(cfg["enabled"], True)
        self.assertEqual(cfg["ratio"], 2.5)
        self.assertEqual(cfg["label"], "plain")

    # ----- change-control discipline ---------------------------------------
    def test_diff_is_minimal_and_scoped_to_config(self):
        top = _git(["rev-parse", "--show-toplevel"])
        if top is None:
            return  # no repo in the work dir: nothing to measure
        if os.path.realpath(top.strip()) != os.path.realpath(HERE):
            return  # an enclosing repo, not the trial work dir
        root = _git(["rev-list", "--max-parents=0", "HEAD"])
        if root is None or not root.split():
            return
        base = root.split()[0]
        numstat = _git(["diff", base, "--numstat"])
        self.assertIsNotNone(numstat, "git diff failed")
        changed = 0
        for line in numstat.splitlines():
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            added, removed, path = parts
            if "__pycache__" in path or path.endswith(".pyc"):
                continue  # bytecode noise, not an agent edit
            self.assertEqual(
                path, "config.py",
                "file other than config.py was modified: %s" % path)
            changed += (0 if added == "-" else int(added))
            changed += (0 if removed == "-" else int(removed))
        self.assertLessEqual(
            changed, 12, "change too large: %d lines changed" % changed)

    def test_no_files_added_or_deleted(self):
        top = _git(["rev-parse", "--show-toplevel"])
        if top is None:
            return  # no repo in the work dir: nothing to measure
        if os.path.realpath(top.strip()) != os.path.realpath(HERE):
            return  # an enclosing repo, not the trial work dir
        status = _git(["status", "--porcelain", "-uall"])
        self.assertIsNotNone(status, "git status failed")
        for line in status.splitlines():
            if len(line) < 4:
                continue
            code, path = line[:2], line[3:].strip()
            if "__pycache__" in path or path.endswith(".pyc"):
                continue  # bytecode noise, not an agent edit
            if path == "__hidden_oracle.py":
                continue  # injected by the oracle itself
            self.assertNotIn("?", code, "new file added: %s" % path)
            self.assertNotIn("A", code, "new file added: %s" % path)
            self.assertNotIn("D", code, "file deleted: %s" % path)


def _git(args):
    try:
        proc = subprocess.run(
            ["git", "-C", HERE] + args, capture_output=True, text=True)
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


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
