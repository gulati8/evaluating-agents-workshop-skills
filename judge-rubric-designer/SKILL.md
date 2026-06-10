---
name: judge-rubric-designer
description: Design LLM-as-judge rubrics for evaluating AI-generated code changes against a codebase's conventions.
---

# Judge Rubric Designer

## Purpose

Some things a deterministic check and a behavioral test cannot settle: whether access is proven on *every* path with the right id, whether an audit record truthfully describes what was written, whether logic is placed at the right altitude, whether raw SQL parameterizes its input. These need a reader — a model that looks at the diff and grades it against explicit criteria.

This skill reads the concerns the earlier layers could not settle and were tagged `judge`, and turns each into a grading rubric: a precise question, concrete pass/fail criteria tied to *this repo's* conventions, the evidence the judge must cite, and the guardrails that keep the judge honest. The rubric is a prompt — a standard written down so it can be applied the same way to every diff.

A judge verdict is probabilistic and the judge is fallible. This skill produces the rubric; it does not establish that the rubric can be trusted. That is the validation layer's job. A rubric here is a candidate standard, not yet a trusted one.

## Inputs

Read the two input file paths given in the prompt — an assertions file (output of the codebase-assertion-designer skill) and a behavioral file (output of the behavioral-evaluation-designer skill). If either path is not given, ask for it. Use:

- from the assertions file: the `escalate` items tagged `target_layer: judge`, and `codebase_profile` (so criteria are grounded in the repo's real conventions, not generic best practice).
- from the behavioral file: the `defer` items tagged `target_layer: judge` (these include the runtime residue behavioral testing could not prove, and the static-only concerns with no runtime signal).

If either file is missing, say so and stop.

## Process

1. Collect every `judge`-tagged concern from both files.
2. Group concerns that protect the same invariant or attach to the same `source_signal` / `source_assertion_id` into one rubric. Do not emit two rubrics for the same dimension — a concern that appears in both layer 01 and layer 02 is one rubric.
3. For each rubric, write the `judge_question` from the concern's `evaluation_question`, made precise.
4. Decompose the question into `grading_criteria` — concrete, individually checkable conditions. Ground each in the repo's actual conventions from `codebase_profile` (name the real symbols, paths, and patterns: `assertPetAccess`, `auditedMutation`, the three public procedures, Zod-source-of-truth, etc.). A criterion a second reader could not apply consistently is too vague — sharpen it.
5. Set `severity` from the source concern: block-derived concerns are `block`; design/convention conformance is usually `warn`.
6. State what evidence the judge must cite (`must_cite`) so a verdict can be checked, not taken on faith.
7. Note the dimension so one judge grades one dimension only.

## Rubric design rules

- **One dimension per judge.** Do not blend authorization correctness with design conformance with test adequacy. Separate rubrics. A single judge asked to weigh everything grades everything worse.
- **Ground criteria in this repo.** "Follows conventions" is not a criterion. "Access is proven via `assertPetAccess` (or a service that calls it) before the first read or write, against the same petId passed to the query" is.
- **Grade the outcome, not a fixed path.** Do not require a specific call order the agent could correctly achieve another way. Require the property to hold.
- **Require citation.** Every verdict must point at the line(s) that justify it. A judge that cannot cite is guessing.
- **Two directions where they exist.** The rubric should be able to fail code that omits the property *and* pass code that satisfies it by a different valid route.
- **Model guidance.** The judge must run on a different and at least as capable model as the one that authored the diff, to avoid a model favoring its own output. Note known biases to resist: preferring longer answers, preferring confident-sounding code, preferring its own style.

## Output handling

Write the full result to the output path given in the prompt, creating any parent directory it names. If no output path is given, ask for one. This file is what the validation layer and the production eval runner read.

After writing, print a short summary to chat: number of judge rubrics, count by severity, the dimensions covered, and the path written. Do not paste the full YAML into chat.

## Output format

Write this structure exactly to the output file:

```yaml
judge_rubrics:
  - id:
    dimension:                 # e.g. authorization_correctness, audit_fidelity, raw_sql_safety, design_conformance
    severity:                  # block | warn
    source_signals:            # list of assertion/defer ids this rubric consolidates
      -
    judge_question:            # the single question the judge answers about a diff
    grading_criteria:          # concrete, repo-grounded, individually checkable
      -
    pass_condition:            # what must hold across criteria to return pass
    must_cite:                 # the evidence the verdict must point at
    verdict_values: [pass, warn, block]
    model_guidance:            # which model to use and biases to resist
    notes:                     # scope and known limits of this rubric

human_only:                    # carry forward target_layer: human items, untouched, so nothing is dropped
  - concern:
    source_signal:
    evaluation_question:
```
