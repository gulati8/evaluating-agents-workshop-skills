---
name: harness-runner
description: Run the full evaluation harness against one code change and produce a single verdict.
---

# Harness Runner

## Purpose

Everything before this evaluates the harness; this runs it. Given one code change — a branch, a commit, or a diff — this skill checks it against all three layers of the evaluation harness and produces a single verdict: pass, or flagged, with each flag naming exactly what tripped and where.

The three layers run cheapest first:

1. **Deterministic assertions** — pattern-level checks of the diff against the assertions file. Did a pet-scoped procedure change without its access check? Did a schema edit ship without a migration? Instant, mechanical.
2. **Behavioral tests** — the repository's own test suite, which now embodies the behavioral layer. Run it; failures are findings.
3. **Judges** — each selected rubric reads the diff against its grading criteria and returns pass or block with cited evidence.

## Inputs

- The change to evaluate: a branch name, commit sha, or diff range given in the prompt. If none is given, ask. Resolve it to a diff against the repository's main branch (or the base the prompt names).
- Assertions file: the path given in the prompt. If none, ask.
- Judges file: the path given in the prompt. If none, ask.
- Output path for the verdict report: given in the prompt. If none, ask.

## Process

### Layer 1 — deterministic assertions

For each assertion in the assertions file, evaluate its `deterministic_signal` against the diff: which files changed, which patterns appear in added/removed lines, which neighboring files did or did not change together. Record fired/clean per assertion. An assertion firing is a finding at that assertion's severity (`block` / `warn` / `info`).

These are evidence checks, not correctness proofs — say so in the report.

### Layer 2 — behavioral tests

Run the repository's test command (discover it from the repo; do not assume). Record pass/fail counts and any failures by name. A failing test is a `block`-level finding. Skipped tests are reported as skipped.

### Layer 3 — judges

For each judge rubric selected (the ids named in the prompt; if none are named, run the `block`-severity rubrics), apply the rubric's `grading_criteria` to the diff and produce a verdict (`pass` or `block`) with the evidence its `must_cite` requires. Follow each rubric's `model_guidance`.

Honesty requirements:
- A judge verdict is probabilistic. Note in the report which judges have been validated against human rulings (if a validation results file is provided in the prompt, read agreement from it) and which are running unvalidated. An unvalidated judge's block is advisory — it is a flag for a human, not a gate.
- The judge must stay scoped to the diff and the files it can see, and must say so when something material is out of view (for example, a guard that moved into a file outside the diff) rather than guessing.

### Verdict

Roll up: the change **passes** if no `block`-level finding fired in any layer. Otherwise it is **flagged**, with findings listed by layer and severity, each naming the file/line or test or criterion that tripped. `warn` and `info` findings are listed but do not block.

## Output handling

Write the full verdict report to the output path. Print a short summary to chat: the verdict, then one line per finding (layer, severity, what tripped). No editorializing, no advice beyond the findings themselves.

## Report format

```markdown
# Harness Verdict — <change>

**Verdict: PASS | FLAGGED**

## Layer 1 — deterministic assertions
<per assertion that fired: id, severity, what tripped, file(s)>
<count of clean assertions>

## Layer 2 — behavioral tests
<command run; passed/failed/skipped counts; failures by name>

## Layer 3 — judges
<per judge: id, validated or unvalidated, verdict, cited evidence>

## Findings
<every block/warn finding, one line each, ordered block first>
```
