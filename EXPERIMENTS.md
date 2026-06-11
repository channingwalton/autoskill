# Experiment log

One entry per run: design, outcome, what it taught us, what to try next.
Detailed in-run reasoning lives in `runs/<id>/mutator-notes.md` and the
ledgers; this file is the cross-run memory.

## exp-1 — Sonnet, scripted loop, cost+quality scoring (2026-06-09 → 10)

- **Design**: trials + mutator `claude-sonnet-4-6` (API), α=0.25, λ=0.02,
  ε=0.05, evolve from empty skill. 10-task suite, 7 optimise / 3 holdout.
- **Outcome**: NULL. 15 iterations, all reject-full, $25.74, zero errored
  trials. Baseline opt +0.862 / holdout +0.927; bar 0.912; candidates ranged
  +0.875 to +0.902.
- **Learned**: Sonnet saturates correctness on this suite — headroom was
  almost all cost-axis. Every candidate beat baseline (15/15 above mean ⇒
  real ~+0.02–0.03 effect, below ε). Mutator converged on "change first, no
  pre-change characterisation tests" and description-only minimal skills —
  rediscovered the standing-token tax. ε was a guess, never calibrated.
- **Next**: quality-only scoring on a model with correctness headroom.

## exp-2 — Qwen3-Coder-Next local, quality-only, skill mechanics (2026-06-10 → 11)

- **Design**: trials + mutator Qwen via llama.cpp `/v1/messages`
  (`base_url`), α=0 (real spend $0), Docker sandbox (work dir only),
  `timeout_multiplier: 6`. Candidate installed as a real skill.
- **Outcome**: NULL, mechanism found. Scripted phase: 10 iterations, plateau
  0.95–0.964 vs bar 0.979 (baseline 0.929). Claude-as-mutator candidates
  c1–c3 likewise failed. **Key finding: the skill body is dead genome** —
  Qwen invoked the Skill tool ~1 time in ~46 trials; only the description
  line is expressed, and even "MANDATORY first step…" descriptions never
  triggered invocation (c3: 0/3).
- **Learned**: (a) opt-in skills do not function for this model under Claude
  Code — a real result about skills on weak models; (b) scripted-phase
  "gains" were description-line domain hints + variance; (c) the scripted
  mutator is structurally blind — failure evidence comes only from the
  champion, never its own rejected candidates; (d) Qwen-as-mutator writes
  task-specific cheat sheets and ignores directive nudges.
- **Next**: deliver the candidate text unconditionally (injection).

## exp-3 — Qwen, injected guidance text (`inject_skill: true`) (2026-06-11, running)

- **Design**: as exp-2 but the candidate body goes in via
  `--append-system-prompt` — unconditionally expressed; measures guidance
  text, not skill mechanics. Claude (Fable 5) is the mutator by hand;
  Qwen runs trials.
- **Protocol amendment (pre-registered before any candidate trial)**:
  identical baselines scored 0.929 (exp-2) vs 0.966 (exp-3) ⇒ single-pass
  aggregates too noisy for ε=0.05, and 0.966+0.05 exceeds the ceiling.
  Amended: baseline = mean of 3 no-skill passes; surviving candidates get 2
  full passes; accept on mean-vs-mean margin (ε_cal = max(0.02, 2×SE)) and
  holdout no-regress on means.
- **Status**: baseline passes 2–3 running. Candidate i1 staged (contract-first:
  enumerate promised behaviours, map promise→code, probe via `python3 -c`
  one-liners, no remembered recipes, minimal change).
- **Outcome**: pending.

## Try-next queue

1. **exp-3 candidates**: i1 first; judge by behaviour change in transcripts
   (probes appearing, edits beyond the obvious function), not score alone.
2. **Fresh holdout tasks**: I (the current mutator) authored the suite, so
   holdout isolation is contaminated for the headline number. Author 3 new
   holdout tasks blind-to-mutator before declaring any exp-3 win.
3. **Scripted-loop evidence fix**: feed the mutator per-task deltas of the
   best rejected candidate + forbid task-specific recipes in the mutation
   prompt. Then rerun an autonomous loop and compare with hand-mutation.
4. **Claude-API mutator vs Qwen mutator** (scripted, injected delivery):
   isolates mutator strength once delivery works.
5. **Suite difficulty**: Qwen baseline ~0.93–0.97 — thin headroom. If exp-3
   nulls at the ceiling, harden tasks (or add tasks where baseline ≤0.8)
   rather than shrinking ε further.
6. **Skill-invocation study (spun off exp-2)**: which models invoke opt-in
   skills at all, and does description wording matter for ones that do?
