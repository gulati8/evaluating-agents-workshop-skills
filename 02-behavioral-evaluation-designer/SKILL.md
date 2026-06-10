---
name: behavioral-evaluation-designer
description: Convert deterministic codebase assertions into behavioral evaluations that prove expected runtime outcomes.
---

# Behavioral Evaluation Designer

## Purpose

A deterministic assertion checks whether a diff touched the expected evidence surface — the right symbol is present, the neighboring file changed. It cannot run the code.

A behavioral evaluation goes one step further: it proves the system actually *behaves* the way the invariant requires, at runtime. "assertPetAccess is in the file" is deterministic. "A non-member calling this procedure is denied" is behavioral — it runs the code and observes the outcome.

This skill reads the deterministic assertions from the previous layer and, for each one worth proving at runtime, designs the test that proves it. It also does something equally important: it states clearly what behavioral testing *still cannot* prove, and routes that to the judge or human layer. Behavioral testing closes part of the gap a deterministic check leaves open — never all of it.

## Inputs

Read the assertions file whose path is given in the prompt (the output of the codebase-assertion-designer skill). If no path is given, ask for one. From it, use:

- `deterministic_assertions` — especially `severity: block` items. Each is a candidate for a behavioral proof.
- the `false_negative_risk` on each assertion — this names what the string-check missed, which is often exactly what a runtime test can prove.
- the `escalate` block — items already tagged `judge` or `human` are concerns no test can settle; carry them forward, do not try to convert them into tests.
- `codebase_profile.tests` — follow the repo's real test conventions (framework, location, naming) so the proposed tests fit where tests actually live.

If the file is missing, say so and stop — this layer depends on it.

## Process

1. Read each deterministic assertion, prioritizing `block` severity.
2. Identify the runtime invariant it protects (often stated in `why_it_matters` and `reviewer_question`).
3. Decide whether that invariant has an *observable runtime behavior*. If yes, design the behavioral evaluation. If no, route it onward.
4. For each behavioral evaluation, include a positive case (the behavior happens when it should) and a negative case (it does not happen when it shouldn't) wherever the invariant has both directions.
5. State the expected result and the evidence that would satisfy the evaluation.
6. For everything behavioral testing cannot settle — including the residue of an assertion you *did* partly cover — write a `defer` entry tagged `judge` or `human`, mirroring the escalate format so the next layer can consume it directly.

## Design rules

Each behavioral evaluation must:

- map back to a deterministic assertion by `source_assertion_id`
- describe an observable system behavior, not a file fact ("file presence does not prove behavior")
- be runnable as an automated test, integration test, API call, or runtime check, in the repo's existing test setup
- state the expected result and the evidence required
- avoid vague criteria like "works correctly" or "is maintainable"

Prefer evaluations that prove: denied access, allowed access, no data leakage, audit row created atomically, schema accepted/rejected, queue producer/consumer match, duplicate action prevented, public contract behavior, dependency/architecture constraint preserved.

Do not convert a subjective concern into a behavioral test. If the real question is "is the code correct on every path" or "is this the right design," that is a `judge` or `human` concern — defer it. A behavioral test proves a behavior on the paths it exercises; it does not prove the absence of a missed path. Be explicit about that limit in the `notes`.

## The defer block

This carries forward what behavioral testing cannot prove, in the same shape as layer 01's `escalate`, so the chain stays consumable:

- `concern`
- `why_not_behavioral`
- `target_layer`: `judge` | `human`
- `source_assertion_id`
- `evaluation_question`

Include both the items inherited from layer 01's `escalate` and any new residue this layer discovers (e.g. "the test proves denial on the read path; whether the write path is also guarded is unproven").

## Output handling

Write the full result to the output path given in the prompt, creating any parent directory it names. If no output path is given, ask for one. This file is what the judge layer and the eval runner read, so write the whole result there.

After writing, print a short summary to chat: number of behavioral evaluations produced, how many have both positive and negative cases, number of `defer` items by `target_layer`, and the path written. Do not paste the full YAML into chat.

## Output format

Write this structure exactly to the output file:

```yaml
behavioral_evaluations:
  - source_assertion_id:
    source_claim:
    protected_invariant:
    evaluations:
      - id:
        behavior:
        direction:            # positive | negative
        test_shape:
        expected_result:
        evidence_required:
        likely_test_location:
        notes:                # state what this proves and, explicitly, what it does not

defer:
  - concern:
    why_not_behavioral:
    target_layer:             # judge | human
    source_assertion_id:
    evaluation_question:
```
