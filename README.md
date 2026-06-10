# autoskill

Evolve an agent skill against a fixed task suite — [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
applied to skill files instead of `train.py`.

A scripted optimisation loop mutates a candidate `SKILL.md`, runs it against a
suite of tasks in isolated headless `claude -p` sessions, scores each trial
mechanically (hidden oracles + cost), and keeps or discards the mutation. Run
it overnight; read the ledger in the morning.

The harness is domain-agnostic: a suite is just a folder of tasks with hidden
oracles (`suites/<name>/`). Anything you can score mechanically can drive the
loop — code tasks, writing tasks with checkable constraints, data wrangling,
tool-use protocols. `suites/software-development/` is the worked example.

The first experiment: evolve a software-development skill **from an empty
start**. Three outcomes are all findings — it reproduces known practice (TDD,
XP), it finds something new, or nothing beats the bare model (the null result:
the skill tax isn't worth paying).

## How it maps to autoresearch

| autoresearch | autoskill |
|---|---|
| `train.py` — the only file the agent mutates | the candidate `SKILL.md` |
| `prepare.py` — fixed harness | `bin/autoskill`, `suites/`, scoring — untouchable during a run |
| 5-minute training budget | per-task `budget_usd` / `max_turns` / `timeout_s` |
| `val_bpb` | hidden-test pass rate − α·cost, aggregated − λ·skill-length penalty |
| `program.md` | `runs/<id>/directives.md` — human-edited, re-read every iteration |

## Layout

- `bin/autoskill` — Python 3 stdlib driver: `init-run`, `check-tasks`, `trial`,
  `suite`, `baseline`, `evolve`
- `suites/<name>/` — a task suite: `suite.yaml` (skill_name, description),
  `directives.md` (default research programme, copied into new runs), and
  `tasks/<id>/` — fixture repo + `prompt.md` + `task.yaml` + hidden oracle +
  reference solution. `holdout: true` tasks gate acceptance and are never shown
  to the mutator.
- `runs/<id>/` — gitignored: config, directives, ledger (append-only JSONL),
  champion, per-trial transcripts and scores
- `skill/autoskill/SKILL.md` — operator skill; symlink into `~/.claude/skills/`

## Quickstart

```sh
bin/autoskill check-tasks                 # validate every suite's oracles both ways
bin/autoskill init-run runs/exp-1 --suite software-development \
  --model claude-sonnet-4-6 --mutator-model claude-sonnet-4-6
# auth: claude setup-token -> save to ~/.config/autoskill/token (chmod 600; NOT in this repo)
bin/autoskill baseline runs/exp-1         # no-skill incumbent over all tasks
bin/autoskill evolve runs/exp-1 --hours 8 # the loop; resumable, just rerun it
tail -f runs/exp-1/ledger.jsonl
```

Models: pick the trial-agent and mutator models at `init-run` (or edit
`config.yaml` before starting). `trial`/`suite` accept a one-off `--model`
override for experiments; `baseline` and `evolve` intentionally do not —
changing the trial model mid-run would void every comparison in the ledger.

Debugging single trials:

```sh
bin/autoskill trial runs/exp-1 <task-id> --no-skill            # bare-model trial
bin/autoskill trial runs/exp-1 <task-id> --candidate <dir>     # dir containing SKILL.md
bin/autoskill suite runs/exp-1 mylabel --no-skill --tasks a,b  # subset, prints aggregate
```

## Authoring a suite

A suite is `suites/<name>/`:

```
suites/<name>/
  suite.yaml        # skill_name: <name the evolved skill gets>, description: <one line>
  directives.md     # default research programme, copied into new runs
  tasks/<task-id>/
    task.yaml       # holdout, budget_usd, max_turns, timeout_s, oracle
    prompt.md       # the user-style prompt the trial agent receives
    fixture/        # the repo the agent works in — hermetic, no network/installs
    oracle/         # oracle.sh + hidden tests — NEVER copied into the sandbox
    solution/       # overlay files: a correct hand-written solution
```

Rules that make the loop trustworthy:

- **Oracle contract**: `oracle.sh <work-dir>` prints one JSON line
  `{"passed": n, "total": m}` as its last stdout line. Nonzero exit ⇒ scored 0.
  Run hidden tests from a scratch copy so the trial agent can neither read nor
  delete them; hidden tests should be a superset of any visible fixture tests
  and cover the edges a lazy solution misses.
- **Both directions**: the oracle must fail on the pristine fixture and pass
  100% on `solution/` overlaid onto the fixture. `bin/autoskill check-tasks
  --suite <name>` verifies exactly this and must be green before any run.
- **Split**: mark ~30% of tasks `holdout: true`. Holdout tasks gate acceptance
  and are never shown to the mutator — they are the only defence against the
  loop memorising the optimise set. Same failure modes, fresh content.
- **Per-task budget**: `budget_usd` normalises the cost term (so one long task
  doesn't dominate) and is charged in full when the real cost is unknowable
  (crash/timeout). The oracle always judges the work dir as-is — running out of
  turns is budget exhaustion, not disqualification.
- The trial harness git-commits the pristine fixture before the agent starts,
  so oracles may inspect `git diff` (e.g. minimal-diff criteria).

## Reading the results

Everything lands in `runs/<id>/`:

- `ledger.jsonl` — one row per iteration: mutation summary, diff stat, stage-1 /
  full / holdout aggregates, verdict (`accept`, `reject-stage1`, `reject-full`,
  `reject-holdout`, `reject-length`), cost. The run header and `baseline` rows
  carry the no-skill incumbent numbers.
- `champion/SKILL.md` + `champion/champion.json` — current best skill and its
  cached scores. The champion's lineage is in `candidates/<iter>/SKILL.md`.
- `trials/<label>/<task>/` — per-trial `transcript.jsonl`, `oracle.json`,
  `score.json` for post-hoc analysis.
- Leak check after a run: `grep -l <holdout-task-id> runs/<id>/candidates/*/mutate-prompt.md`
  must return nothing.

Interpreting the outcome: a champion that beats baseline on opt **and** holdout
is a real (suite-level) win; a flat trajectory with healthy trials is the null
result — no skill beat the bare model, the skill tax isn't worth paying. Check
trial error rates before declaring either: auth failures and broken oracles
also produce flat trajectories.

## The loop, per iteration

1. **Mutate** — one `claude -p` call sees the champion skill, the human
   directives, the recent ledger tail, and failure evidence from the champion's
   worst optimise-set tasks. It writes one revised `SKILL.md` (one change;
   deletions preferred; 400-line hard cap).
2. **Stage 1** — 3 rotating optimise tasks. Clearly worse than champion ⇒ reject.
3. **Full optimise set** — must beat the champion's aggregate by ε.
4. **Holdout gate** — must not regress on the held-out tasks. Holdout results
   are recorded but never fed back into mutation.
5. **Accept** ⇒ new champion. Everything lands in `ledger.jsonl`.

Stops on max iterations, budget, reject streak, or deadline. Crash-safe:
`evolve` resumes from the ledger.

## Safety notes

- Trials run with `--dangerously-skip-permissions` in a throwaway temp dir, but
  that is **not** a sandbox — the trial agent can reach the network and the
  wider filesystem. Containerising trials is future work.
- Trials use an isolated `CLAUDE_CONFIG_DIR` so your global CLAUDE.md, skills,
  hooks and MCP servers cannot contaminate the experiment. Keychain auth does
  not carry over: mint a token with `claude setup-token` and keep it **outside
  the repo** — `~/.config/autoskill/token` (or `$AUTOSKILL_TOKEN_FILE`, or
  export `CLAUDE_CODE_OAUTH_TOKEN`). Nothing under the repo ever holds a
  credential, so pushing to GitHub is safe.
- An overnight run spends real money. Set `max_budget_usd` in `config.yaml`
  deliberately; expect roughly $2–3 per iteration at sonnet-class trial models.

## Anti-gaming

- Oracles are hidden: tests live outside the trial sandbox and a superset of
  any visible fixture tests.
- `check-tasks` proves every oracle fails on the pristine fixture and passes on
  the reference solution.
- The cost term and λ length penalty push against ritual and bloat; the holdout
  gate pushes against memorising the optimise set.
