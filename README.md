# Evaluating Agents — Workshop Skills

A set of six [Claude Code skills](https://docs.claude.com/en/docs/claude-code/skills) that compose into a **layered evaluation harness** for AI‑generated code changes. Built for the *"From Agent User to Agent Architect"* workshop, where the central problem is: once agents start writing code, **how do you know when to trust a change?**

The harness answers that by checking a diff at three escalating levels of rigor — cheap mechanical checks first, runtime proof next, and human‑calibrated model judgment last — and producing a single verdict with every flag traced back to exactly what tripped it.

## The core idea

No single check can tell you a generated change is trustworthy. A string match can confirm the right symbol is present but can't run the code. A test can prove behavior but can't reason about design. A model can judge design but is fallible until validated. So the harness layers them, **cheapest first**, and each layer explicitly hands off what it *can't* settle to the next:

| Layer | Question it answers | Cost | Certainty |
|-------|--------------------|------|-----------|
| **1 — Deterministic** | Did the change carry the *evidence* a trustworthy change would? | Machine‑speed | Mechanical, no judgment |
| **2 — Behavioral** | Does the code actually *behave* the way the invariant requires, at runtime? | Test‑suite | Proven, where runtime‑observable |
| **3 — Judge** | Is what's left correct, well‑designed, secure? | Model call | Probabilistic, must be validated |

The handoff is the whole point: each layer names what it leaves open and tags it for the layer that can handle it, so nothing falls through the cracks and no layer pretends to a certainty it doesn't have.

## The skills

The six skills split into **design‑time** (build and calibrate the harness for a repo, run once) and **run‑time** (evaluate a change, run on every diff).

### Design‑time — build the harness

| Skill | Input → Output |
|-------|----------------|
| **`codebase-assertion-designer`** | a repository → a **codebase profile** + **deterministic assertions** (Layer 1). Profiles the repo's real conventions and high‑risk surfaces; everything downstream builds on this. Concerns needing judgment go in an `escalate` block tagged for a later layer. |
| **`behavioral-evaluation-designer`** | assertions file → **behavioral evaluation specs** (Layer 2). For each assertion worth proving at runtime, designs the test that proves it — and states clearly what runtime testing still *can't* prove, routing that onward. |
| **`behavioral-test-implementer`** | behavioral specs + repo → **real test files, run**. Inspects how the repo actually writes and runs tests, writes tests in that style, runs them, and reports honestly what passed, failed, or needs infrastructure it doesn't fake. |
| **`judge-rubric-designer`** | assertions + behavioral files → **LLM‑as‑judge rubrics** (Layer 3). Turns every `judge`‑tagged concern into a precise grading rubric grounded in *this* repo's conventions: one dimension per judge, criteria a second reader could apply, required citations. |
| **`judge-validation-runner`** | a rubric + recent real commits → **agreement score + rubric fixes**. A rubric is a candidate standard until measured. Runs the judge on real history, has a human rule on each (human = ground truth), and turns every disagreement into a specific fix. |

### Run‑time — evaluate a change

| Skill | Input → Output |
|-------|----------------|
| **`harness-runner`** | a branch / commit / diff + assertions + judges → a **single verdict** (`pass` or `flagged`). Runs all three layers cheapest‑first and reports each flag with exactly what tripped and where. |

## How they fit together

```
                          ┌─────────────────────────────┐
   repository ──────────► │  codebase-assertion-designer │  Layer 1
                          └───────────────┬─────────────┘
                                          │ assertions + codebase profile
                  ┌───────────────────────┼───────────────────────┐
                  ▼                        ▼                        │
   ┌──────────────────────────┐   (escalate: judge)                │
   │ behavioral-evaluation-    │   Layer 2 specs                   │
   │ designer                  │                                    │
   └────────────┬─────────────┘                                    │
                │ behavioral specs                                  │
                ▼                          ▼                        │
   ┌──────────────────────────┐   ┌──────────────────────────┐    │
   │ behavioral-test-          │   │ judge-rubric-designer     │ ◄──┘
   │ implementer (real tests)  │   │ Layer 3 rubrics           │
   └──────────────────────────┘   └────────────┬─────────────┘
                                                │ rubrics
                                                ▼
                                   ┌──────────────────────────┐
                                   │ judge-validation-runner   │  trust the judges
                                   └────────────┬─────────────┘
                                                │ validated rubrics
   ────────────────────────────────────────────┼────────────────────────────
                                                ▼
   a code change ─────────────────►  ┌──────────────────────────┐
                                      │      harness-runner       │  → verdict
                                      └──────────────────────────┘
```

A typical end‑to‑end flow:

1. **Profile the repo** with `codebase-assertion-designer` → assertions + profile.
2. **Design behavioral evals** with `behavioral-evaluation-designer` from those assertions.
3. **Implement and run** those tests with `behavioral-test-implementer`.
4. **Design judge rubrics** with `judge-rubric-designer` from the `judge`‑tagged residue of layers 1 and 2.
5. **Validate the judges** against real commits with `judge-validation-runner` until their verdicts can be trusted.
6. **Evaluate every change** with `harness-runner`, which runs all three layers and emits one verdict.

## Repository layout

```
.
├── behavioral-evaluation-designer/SKILL.md
├── behavioral-test-implementer/SKILL.md
├── codebase-assertion-designer/SKILL.md
├── harness-runner/SKILL.md
├── judge-rubric-designer/SKILL.md
└── judge-validation-runner/SKILL.md
```

Each skill is a single `SKILL.md` with YAML frontmatter (`name`, `description`) and the instructions Claude follows when the skill is invoked.

## Using the skills

Drop the skill directories into a Claude Code skills location — `.claude/skills/` in a project, or `~/.claude/skills/` for global use — and invoke them by name (e.g. `/codebase-assertion-designer`). Most skills take and produce file paths so their outputs chain into the next skill's inputs; if a path isn't given, the skill asks for one.

## Design principles

- **Cheapest check first.** Run mechanical checks before tests before model calls; stop spending when a cheap layer settles it.
- **Honest handoffs.** Every layer names what it can't prove and routes it onward — no layer claims certainty it doesn't have.
- **Grounded in the real repo.** Criteria reference the repository's actual symbols, paths, and conventions, not generic best practice.
- **Judges must earn trust.** A rubric is a candidate standard until validated against real commits with a human as ground truth.
- **No faked passes.** A test that needs infrastructure is marked pending, not hidden; a failing test is a finding, not noise.

---

Part of the [*From Agent User to Agent Architect*](../) workshop materials.
