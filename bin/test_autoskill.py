#!/usr/bin/env python3
"""Unit tests for bin/autoskill. No API calls — pure functions and file plumbing."""

import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module():
    spec = importlib.util.spec_from_loader(
        "autoskill_mod",
        importlib.machinery.SourceFileLoader("autoskill_mod", os.path.join(HERE, "autoskill")),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


a = load_module()


class TestParseKv(unittest.TestCase):
    def test_types_and_comments(self):
        text = """
# comment
model: claude-sonnet-4-6
alpha: 0.25
max_turns: 25
holdout: true
quoted: "hello: world"
"""
        out = a.parse_kv_text(text)
        self.assertEqual(out["model"], "claude-sonnet-4-6")
        self.assertEqual(out["alpha"], 0.25)
        self.assertEqual(out["max_turns"], 25)
        self.assertIs(out["holdout"], True)
        self.assertEqual(out["quoted"], "hello: world")


class TestScoring(unittest.TestCase):
    def test_task_score_basics(self):
        # full pass, no cost
        self.assertAlmostEqual(a.task_score(4, 4, 0.0, 0.5, 0.25), 1.0)
        # full pass at exactly budget: 1 - 0.25
        self.assertAlmostEqual(a.task_score(4, 4, 0.5, 0.5, 0.25), 0.75)
        # cost capped at 1.5x budget
        self.assertAlmostEqual(a.task_score(4, 4, 5.0, 0.5, 0.25), 1.0 - 0.25 * 1.5)
        # zero total -> zero success
        self.assertAlmostEqual(a.task_score(0, 0, 0.0, 0.5, 0.25), 0.0)

    def test_skill_penalty_and_aggregate(self):
        self.assertEqual(a.skill_penalty("", 0.02), 0.0)
        text = "x" * 4000  # ~1k tokens
        self.assertAlmostEqual(a.skill_penalty(text, 0.02), 0.02)
        self.assertAlmostEqual(a.aggregate([1.0, 0.5], text, 0.02), 0.75 - 0.02)
        self.assertEqual(a.aggregate([], "anything", 0.02), 0.0)


class TestValidateCandidate(unittest.TestCase):
    GOOD = "---\nname: dev\ndescription: use for dev tasks\n---\n\n# Skill\nbody\n"

    def test_valid(self):
        ok, reason = a.validate_candidate(self.GOOD, 400)
        self.assertTrue(ok, reason)

    def test_too_long(self):
        ok, reason = a.validate_candidate(self.GOOD + "x\n" * 400, 400)
        self.assertEqual((ok, reason), (False, "reject-length"))

    def test_missing_frontmatter(self):
        ok, reason = a.validate_candidate("# no frontmatter\n", 400)
        self.assertEqual((ok, reason), (False, "reject-frontmatter"))

    def test_unclosed_frontmatter(self):
        ok, reason = a.validate_candidate("---\nname: x\n", 400)
        self.assertEqual((ok, reason), (False, "reject-frontmatter"))

    def test_missing_description(self):
        ok, reason = a.validate_candidate("---\nname: x\n---\nbody\n", 400)
        self.assertEqual((ok, reason), (False, "reject-frontmatter"))

    def test_frontmatter_name(self):
        self.assertEqual(a.frontmatter_name(self.GOOD, "fallback"), "dev")
        self.assertEqual(a.frontmatter_name("junk", "fallback"), "fallback")


class TestTranscriptParsing(unittest.TestCase):
    def test_result_event(self):
        lines = [
            json.dumps({"type": "system", "subtype": "init"}),
            "not json",
            json.dumps({"type": "assistant", "message": {}}),
            json.dumps({"type": "result", "total_cost_usd": 0.12,
                        "num_turns": 7, "is_error": False, "result": "done"}),
        ]
        out = a.parse_transcript_result(lines)
        self.assertEqual(out, {"cost_usd": 0.12, "num_turns": 7,
                               "is_error": False, "final_message": "done",
                               "has_activity": True})

    def test_missing_result_is_error(self):
        out = a.parse_transcript_result([json.dumps({"type": "assistant"})])
        self.assertTrue(out["is_error"])
        self.assertIsNone(out["cost_usd"])
        self.assertTrue(out["has_activity"])

    def test_no_activity_without_assistant_events(self):
        out = a.parse_transcript_result([json.dumps({"type": "system"})])
        self.assertFalse(out["has_activity"])


class TestAcceptRule(unittest.TestCase):
    def test_must_beat_champion_by_epsilon(self):
        # equal -> reject; epsilon edge -> reject; above -> accept path
        self.assertEqual(a.accept_verdict(0.50, 0.5, 0.50, 0.5, 0.05), "reject-full")
        self.assertEqual(a.accept_verdict(0.55, 0.5, 0.50, 0.5, 0.05), "reject-full")
        self.assertEqual(a.accept_verdict(0.56, 0.5, 0.50, 0.5, 0.05), "accept")

    def test_holdout_gate(self):
        # wins optimise but regresses holdout beyond epsilon
        self.assertEqual(a.accept_verdict(0.7, 0.40, 0.5, 0.5, 0.05), "reject-holdout")
        # holdout within epsilon tolerance is fine
        self.assertEqual(a.accept_verdict(0.7, 0.46, 0.5, 0.5, 0.05), "accept")

    def test_stage1(self):
        self.assertEqual(a.stage1_verdict(0.40, 0.5, 0.05), "reject-stage1")
        # stage1 only needs to be within epsilon of champion, not beat it
        self.assertEqual(a.stage1_verdict(0.46, 0.5, 0.05), "continue")


class TestStage1Rotation(unittest.TestCase):
    def test_rotates_and_wraps(self):
        ids = ["a", "b", "c", "d", "e", "f", "g"]
        s1 = a.stage1_tasks(ids, 1, 3)
        s2 = a.stage1_tasks(ids, 2, 3)
        self.assertEqual(len(s1), 3)
        self.assertNotEqual(s1, s2)
        # wraps around the end of the list
        self.assertEqual(a.stage1_tasks(ids, 2, 3), ["g", "a", "b"])
        # deterministic
        self.assertEqual(a.stage1_tasks(ids, 5, 3), a.stage1_tasks(ids, 5, 3))

    def test_smaller_pool_than_size(self):
        self.assertEqual(a.stage1_tasks(["a", "b"], 3, 3), ["a", "b"])
        self.assertEqual(a.stage1_tasks([], 3, 3), [])


class TestLedgerResume(unittest.TestCase):
    def entries(self):
        return [
            {"type": "run-header"},
            {"type": "baseline", "cost_usd": 2.0},
            {"type": "iter-start", "iter": 1},
            {"type": "iteration", "iter": 1, "verdict": "reject-full", "iter_cost_usd": 1.5},
            {"type": "iter-start", "iter": 2},
            {"type": "iteration", "iter": 2, "verdict": "accept", "iter_cost_usd": 2.5},
            {"type": "iter-start", "iter": 3},
            {"type": "iteration", "iter": 3, "verdict": "reject-stage1", "iter_cost_usd": 0.5},
            # crash: iter 4 started, never finished
            {"type": "iter-start", "iter": 4},
        ]

    def test_resume(self):
        next_iter, rejects, spent = a.resume_state(self.entries())
        self.assertEqual(next_iter, 4)  # incomplete iter 4 is re-run
        self.assertEqual(rejects, 1)    # streak resets at the accept
        self.assertAlmostEqual(spent, 6.5)

    def test_empty_ledger(self):
        self.assertEqual(a.resume_state([]), (1, 0, 0.0))

    def test_roundtrip_files(self):
        with tempfile.TemporaryDirectory() as run_dir:
            a.append_ledger(run_dir, {"type": "iteration", "iter": 1,
                                      "verdict": "accept", "iter_cost_usd": 1.0})
            entries = a.read_ledger(run_dir)
            self.assertEqual(len(entries), 1)
            self.assertIn("ts", entries[0])


class TestChampionRoundtrip(unittest.TestCase):
    def test_write_read(self):
        with tempfile.TemporaryDirectory() as run_dir:
            meta = {"iter": 3, "opt_agg": 0.5, "holdout_agg": 0.4,
                    "per_task": {"a": 0.5}, "trials_label": "3-full"}
            a.write_champion(run_dir, meta, "---\nname: x\ndescription: y\n---\nbody")
            champ = a.read_champion(run_dir)
            self.assertEqual(champ["iter"], 3)
            self.assertIn("body", champ["skill_text"])

    def test_empty_skill_baseline(self):
        with tempfile.TemporaryDirectory() as run_dir:
            a.write_champion(run_dir, {"iter": 0, "opt_agg": 0.1,
                                       "holdout_agg": 0.1, "per_task": {}}, "")
            champ = a.read_champion(run_dir)
            self.assertEqual(champ["skill_text"], "")


class TestDiffStat(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(a.diff_stat("a\nb\n", "a\nc\nd\n"), "+2 -1")
        self.assertEqual(a.diff_stat("same\n", "same\n"), "+0 -0")


class TestOracleParsing(unittest.TestCase):
    def write_oracle(self, tmp, script):
        path = os.path.join(tmp, "oracle.sh")
        with open(path, "w") as f:
            f.write(script)
        return path

    def test_good_oracle(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_oracle(tmp, 'echo \'{"passed": 3, "total": 4}\'\n')
            self.assertEqual(a.run_oracle(path, tmp), {"passed": 3, "total": 4})

    def test_nonzero_exit_zeroes_passed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_oracle(tmp, 'echo \'{"passed": 3, "total": 4}\'\nexit 1\n')
            out = a.run_oracle(path, tmp)
            self.assertEqual(out["passed"], 0)
            self.assertEqual(out["total"], 4)

    def test_garbage_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_oracle(tmp, "echo not-json\n")
            out = a.run_oracle(path, tmp)
            self.assertEqual(out["passed"], 0)
            self.assertIn("error", out)


class TestInfraFailure(unittest.TestCase):
    def test_usage_limit_is_infra(self):
        self.assertTrue(a.is_infra_failure(
            {"is_error": True, "cost_usd": 0,
             "final_message": "Claude usage limit reached. Your limit will reset at 5pm"}))

    def test_not_logged_in_is_infra(self):
        self.assertTrue(a.is_infra_failure(
            {"is_error": True, "cost_usd": None,
             "final_message": "Not logged in · Please run /login"}))

    def test_real_failure_with_cost_is_not_infra(self):
        # max-turns exhaustion spent money: a genuine attempt, score it
        self.assertFalse(a.is_infra_failure(
            {"is_error": True, "cost_usd": 0.18,
             "final_message": "usage limit"}))

    def test_unrecognised_zero_cost_error_is_not_infra(self):
        rec = {"is_error": True, "cost_usd": 0, "final_message": "model not found"}
        self.assertFalse(a.is_infra_failure(rec))
        self.assertTrue(a.is_zero_cost_error(rec))

    def test_success_is_neither(self):
        rec = {"is_error": False, "cost_usd": 0.1, "final_message": "done"}
        self.assertFalse(a.is_infra_failure(rec))
        self.assertFalse(a.is_zero_cost_error(rec))

    def test_local_trial_with_activity_is_honest_failure(self):
        # base_url runs record cost 0 always — assistant activity proves
        # real work, so an errored/timed-out trial is scored, not retried
        rec = {"is_error": True, "cost_usd": 0.0, "cost_reported": None,
               "has_activity": True, "final_message": "usage limit"}
        self.assertFalse(a.is_infra_failure(rec))
        self.assertFalse(a.is_zero_cost_error(rec))

    def test_local_fictional_cost_counts_as_work(self):
        rec = {"is_error": True, "cost_usd": 0.0, "cost_reported": 0.14,
               "has_activity": False, "final_message": "service unavailable"}
        self.assertFalse(a.is_infra_failure(rec))
        self.assertFalse(a.is_zero_cost_error(rec))


class TestClaudeEnv(unittest.TestCase):
    def test_base_url_never_carries_oauth_token(self):
        with tempfile.TemporaryDirectory() as run_dir:
            old = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
            os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = "sk-real-secret"
            try:
                env = a.claude_env(run_dir, {"base_url": "http://127.0.0.1:8080"})
            finally:
                if old is None:
                    del os.environ["CLAUDE_CODE_OAUTH_TOKEN"]
                else:
                    os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = old
            self.assertEqual(env["ANTHROPIC_BASE_URL"], "http://127.0.0.1:8080")
            self.assertEqual(env["ANTHROPIC_AUTH_TOKEN"], "local")
            self.assertNotIn("CLAUDE_CODE_OAUTH_TOKEN", env)

    def test_no_base_url_keeps_token_path(self):
        with tempfile.TemporaryDirectory() as run_dir:
            env = a.claude_env(run_dir, {})
            self.assertNotIn("ANTHROPIC_BASE_URL", env)


class TestSkillBody(unittest.TestCase):
    def test_strips_frontmatter(self):
        text = "---\nname: x\ndescription: y\n---\n\n# Body\n\nRule one.\n"
        self.assertEqual(a.skill_body(text), "# Body\n\nRule one.\n")

    def test_no_frontmatter_passthrough(self):
        self.assertEqual(a.skill_body("plain text\n"), "plain text\n")

    def test_unclosed_frontmatter_passthrough(self):
        text = "---\nname: x\nno closing fence\n"
        self.assertEqual(a.skill_body(text), text)


class TestDockerCmd(unittest.TestCase):
    CONFIG = {"docker_image": "autoskill-trial",
              "base_url": "http://127.0.0.1:8080"}

    def test_rewrites_loopback_for_container(self):
        self.assertEqual(a.container_base_url("http://127.0.0.1:8080"),
                         "http://host.docker.internal:8080")
        self.assertEqual(a.container_base_url("http://localhost:1234/v1"),
                         "http://host.docker.internal:1234/v1")

    def test_mounts_only_work_dir(self):
        with tempfile.TemporaryDirectory() as work:
            env = {"ANTHROPIC_BASE_URL": "http://127.0.0.1:8080",
                   "ANTHROPIC_AUTH_TOKEN": "local"}
            cmd = a.docker_cmd(self.CONFIG, work, env, ["claude", "-p", "x"],
                               "autoskill-test")
            mounts = [cmd[i + 1] for i, t in enumerate(cmd) if t == "-v"]
            self.assertEqual(mounts, [os.path.realpath(work) + ":/work"])
            joined = " ".join(cmd)
            self.assertIn("ANTHROPIC_BASE_URL=http://host.docker.internal:8080",
                          joined)
            self.assertNotIn("CLAUDE_CODE_OAUTH_TOKEN", joined)
            # image then the claude args, nothing after
            self.assertEqual(cmd[-4:], ["autoskill-trial", "claude", "-p", "x"])


class TestWaitForCapacity(unittest.TestCase):
    CONFIG = {"limit_poll_minutes": 15, "limit_max_wait_hours": 1, "model": "m"}

    def test_returns_when_probe_recovers(self):
        sleeps = []
        probes = iter([False, False, True])
        a.wait_for_capacity("unused-run", self.CONFIG,
                            sleep_fn=sleeps.append, probe_fn=lambda: next(probes))
        self.assertEqual(len(sleeps), 3)
        self.assertEqual(sleeps[0], 15 * 60)

    def test_raises_past_max_wait(self):
        with self.assertRaises(a.StopRun):
            a.wait_for_capacity("unused-run", self.CONFIG,
                                sleep_fn=lambda s: None, probe_fn=lambda: False)

    def test_raises_at_deadline(self):
        import datetime
        past = datetime.datetime.now() - datetime.timedelta(seconds=1)
        with self.assertRaises(a.StopRun):
            a.wait_for_capacity("unused-run", self.CONFIG, deadline=past,
                                sleep_fn=lambda s: None, probe_fn=lambda: False)


if __name__ == "__main__":
    unittest.main()
