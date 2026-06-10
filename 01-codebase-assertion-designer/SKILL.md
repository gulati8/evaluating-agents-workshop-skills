---
name: codebase-assertion-designer
description: Inspect a codebase and propose deterministic assertions for evaluating future AI-generated code changes.
---

# Codebase Assertion Designer

## Purpose

Read a codebase and produce two things:

1. A **codebase profile** — the conventions, patterns, and high-risk surfaces this repository actually uses. This profile is the foundation every later evaluation stage builds on, so it must describe what is *true of this repo*, not generic best practice.
2. A set of **deterministic assertions** — cheap, mechanical checks that a future AI-generated diff can be tested against without human judgment.

A deterministic assertion does not prove the code is correct. It checks whether a change carried the *evidence* a trustworthy change would carry — the right files touched, the expected symbols present, the neighboring files updated together. It tells a reviewer where to look, and it runs on every diff at machine speed.

Anything that needs judgment about whether the code is actually correct, well-designed, or secure does **not** belong in a deterministic assertion. It belongs in the `escalate` block, tagged for the layer that can handle it. That handoff is what lets a judge or a human pick up exactly where the mechanical check stops.

## When to use this skill

Use when asked to:

- design deterministic assertions for a repository
- profile a codebase's conventions or high-risk change surfaces
- set up automated evidence checks for future generated diffs
- build the first (deterministic) layer of an agent-code evaluation harness

Do not require a specific feature request — work from repository structure.

## Process

1. Inspect the repository structure and identify the architecture and major layers.
2. Identify where tests live and how they are named.
3. Identify authorization, permissions, and access-control patterns.
4. Identify data model, schema, and migration patterns.
5. Identify API, route, controller, schema, and contract patterns.
6. Identify logging, audit, metrics, and observability patterns.
7. Identify dependency, package, build, and configuration files.
8. Identify the high-risk change surfaces — where a silent mistake would be expensive.
9. Propose deterministic assertions tied directly to the observed structure.
10. For every concern you could see but could not make mechanical, write an `escalate` entry tagged `judge` or `human`.

## Assertion design rules

Each assertion must be checkable mechanically against a future diff. Good signals include:

- specific directories or file types touched
- required neighboring files changed together
- expected keywords or symbols present
- test files added or modified
- dependency, migration, or API-contract files changed
- authorization, audit, or logging surfaces touched

Do **not** write assertions that require judgment — "abstraction is good," "logic is correct," "tests are sufficient," "code is maintainable." Those are not failures of the assertion; they are the boundary of what is mechanical. Send each one to the `escalate` block instead.

For every assertion, be honest about its limits: state the `false_positive_risk` (where it fires but nothing is wrong) and the `false_negative_risk` (where it passes but something could still be wrong). The false-negative is usually the reason a downstream judge or human layer exists — name it so the handoff is explicit.

## Severity definitions

- `block`: a missing signal should stop normal review unless explained or overridden. Reserve for high-risk surfaces (authz, audit, schema, public API).
- `warn`: a missing signal should focus reviewer attention.
- `info`: useful context, not a gate.

## The escalate block

This is the bridge to the rest of the harness. Every concern you cannot make deterministic goes here, with:

- `concern`: what needs evaluating
- `why_not_deterministic`: why a mechanical check cannot answer it
- `target_layer`: `judge` if a model reading the diff against criteria could evaluate it; `human` if it depends on intent, architecture direction, or context not present in the code
- `source_signal`: the assertion id or repo surface this concern attaches to, so the next stage knows where it lives
- `evaluation_question`: the question the next layer must answer (for `judge` items, this becomes the judge's grading question)

Tag `judge` for things like "is access proven on every path," "does this follow the repo's established pattern." Tag `human` for things like "is this the right architecture for where we're heading," "does this test reflect what the feature was meant to do."

## Inputs and outputs

This skill reads the repository in the working directory; it takes no input file.

Write the whole result to the output path given in the prompt, creating any parent directory it names. If no output path is given, ask for one rather than guessing a filename. The full result must go to the file — it is what later stages read — not only to chat.

After writing, print a short summary to the conversation: the number of assertions by severity (`block`/`warn`/`info`), the number of `escalate` items by `target_layer`, and the path written. Do not paste the full YAML into chat — the file is the source of truth; the summary is just for a quick eyeball.

## Output format

Write this structure exactly to the output file:

```yaml
codebase_profile:
  architecture:
    - observation:
  tests:
    - observation:
  authorization:
    - observation:
  data_access:
    - observation:
  api_contracts:
    - observation:
  observability:
    - observation:
  dependencies:
    - observation:

deterministic_assertions:
  - id:
    name:
    category:
    severity:           # block | warn | info
    claim:
    deterministic_signal:
    files_or_patterns_to_inspect:
      files:
        -
      patterns:
        -
    why_it_matters:
    false_positive_risk:
    false_negative_risk:
    reviewer_question:

escalate:
  - concern:
    why_not_deterministic:
    target_layer:         # judge | human
    source_signal:        # assertion id or repo surface this attaches to
    evaluation_question:
```
