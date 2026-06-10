---
name: autoskill
description: >-
  Operate the autoskill harness at ~/dev/autoskill: evolve a skill against the
  fixed task suite via overnight optimisation runs. Use when the user says
  "autoskill", "evolve a skill", "run the skill evolution", "check on the
  evolution run", or asks to analyse a finished run. Not for editing the
  harness itself, authoring ordinary skills, or single code reviews.
---

# Autoskill Operator

You operate a fixed harness; you do not improvise around it. The harness
(`bin/autoskill`, `tasks/`, scoring) is the experiment's `prepare.py` — during a
run it is untouchable. The only thing that evolves is the candidate `SKILL.md`,
and the only state is the run's `ledger.jsonl`.

All commands run from the repo root `~/dev/autoskill`.

## Hard rules

- **Never edit `bin/`, `tasks/`, scoring, or `config.yaml` while a run is in
  progress.** Changing the instrument mid-experiment voids every comparison in
  the ledger. Finish or kill the run first, and say so in the ledger analysis.
- **Never surface holdout task content** (`tasks/*/` with `holdout: true`) into
  `directives.md`, mutation prompts, or any analysis the mutator might later
  see. The holdout gate is the only defence against overfitting the suite.
- **Never launch `evolve` without a green smoke check** (steps below). A broken
  oracle or auth failure burns the budget producing garbage verdicts.
- Report costs honestly from the ledger; never estimate when the ledger has
  the number.

## 🎯 CONFIGURE

1. Pick the suite (`suites/<name>/`, or author a new one for a new domain).
   `bin/autoskill check-tasks --suite <name>` — every task must report `ok`.
   A task failing either direction (passes on pristine, or fails on solution)
   is a broken oracle: fix the task, not the harness.
2. `bin/autoskill init-run runs/<name> --suite <suite>` — then edit:
   - `config.yaml`: trial + mutator model, ε, α, λ, `max_iterations`,
     `max_budget_usd` (confirm the budget with the user — this is real spend),
     stop criteria.
   - `directives.md`: the research programme. Keep it short; it is re-read
     every iteration, so mid-run steering happens here and only here.
3. Auth: the isolated `CLAUDE_CONFIG_DIR` cannot see Keychain credentials.
   Have the user run `claude setup-token` and save the token to
   `~/.config/autoskill/token` (chmod 600) — never anywhere under the repo.
4. Smoke check: one cheap trial —
   `bin/autoskill trial runs/<name> <some-task> --no-skill` — and confirm the
   score JSON has a real `cost_usd` and no `is_error`.

## 📏 BASELINE

`bin/autoskill baseline runs/<name>` — the no-skill incumbent over the full
suite. Record the opt and holdout aggregates in conversation. Every future
champion must beat this; if nothing ever does, that is the null result and it
is a finding, not a failure.

## 🧬 EVOLVE

- Launch in the background: `bin/autoskill evolve runs/<name> --hours <H>`.
- Monitor from the ledger only: `tail runs/<name>/ledger.jsonl`. Do not read
  trial transcripts mid-run into context; they are large and the ledger row
  already carries the verdict.
- The loop is resumable — after a crash or kill, rerun the same command;
  incomplete iterations re-run automatically.
- Mid-run steering = edit `directives.md`. Nothing else.

## 🔍 ANALYSE

From the ledger (`jq` over `ledger.jsonl`):

1. Trajectory: champion aggregate over iterations vs baseline, opt and holdout.
2. Verdict mix: accepts / reject-stage1 / reject-full / reject-holdout /
   reject-length. A high reject-holdout rate = the loop is memorising the
   suite. A high reject-length rate = mutation pressure is bloating.
3. Champion lineage: diff each accepted candidate
   (`runs/<name>/candidates/<iter>/SKILL.md`) against its parent — what
   actually accumulated?
4. Cost: total spend, spend per accept.
5. Holdout-leak check: `grep -l <holdout-task-ids> runs/<name>/candidates/*/mutate-prompt.md`
   must return nothing.

## 📊 REPORT

Present inline:

```
## Run <name>
Baseline (no skill): opt <x>, holdout <y>
Final champion: iter <n>, opt <x>, holdout <y>  (Δ vs baseline)
Iterations: <n> (<a> accepts, <r> rejects by class)
Spend: $<total> ($<per-accept> per accept)

## What evolved
<the champion SKILL.md, annotated: which iteration added/removed each part, and
 what evidence drove it>

## Verdict
<one of: reproduced known practice (name it) | novel structure (describe it) |
 null result — no skill beat the bare model. State which, with the numbers.>

## Next
<directives changes, task-suite gaps, or "promote champion for real-world use
 behind a retrospective VERIFY window">
```

A champion that wins here has won on a synthetic suite. Before promoting it to
real use, hand it to the retrospective skill's VERIFY loop: did it reduce
cost on real sessions? The suite is the training distribution; real work is the
test set.

## Red flags

- Editing the harness or tasks mid-run to "help" a struggling candidate.
- Reading holdout fixtures, then writing directives — you are now the leak.
- Treating a noisy single-iteration win as progress; only the accept rule
  (ε + holdout gate) decides.
- Letting a run continue past its budget because it "looks close".
- Declaring the null result without a healthy run (auth failures and broken
  oracles also produce flat trajectories — check error rates first).
