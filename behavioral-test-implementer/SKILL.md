---
name: behavioral-test-implementer
description: Turn behavioral evaluation specs into real tests in a repository's existing test suite and run them.
---

# Behavioral Test Implementer

## Purpose

The behavioral layer of the harness exists only as descriptions until someone writes real tests. This skill does that: it reads the behavioral evaluation specs, inspects how the repository actually writes and runs tests, writes real test files that match those conventions, runs them, and reports honestly what passed, failed, or could not run.

It does not invent a test framework or a database setup. It uses what the repository already has. Where a spec needs infrastructure the repository's test setup does not provide (for example a live database for a real rollback), it writes the test but marks it clearly as not-yet-runnable rather than letting it fail silently or faking a pass.

## Inputs

- Behavioral file: the path given in the prompt (the output of the behavioral-evaluation-designer skill). If no path is given, ask for one.
- The repository in the working directory.

## Process

1. **Look at the real test setup first. Do not assume.** Inspect the repository: find existing test files, the test framework, how tests build fixtures and contexts (a real database, an in-memory one, or mocks), and the command that runs the suite. Match whatever is actually there. If the behavioral spec assumed mocks but the repo uses a real test database, follow the repo, not the spec.

2. **Sort the specs into runnable-now and needs-infrastructure.** A spec is runnable-now if the repo's existing test setup can execute it as-is (most logic-level behaviors: access denied, access allowed, wrong-role rejected). A spec needs-infrastructure if it requires something the test setup does not currently provide — a live database for true transaction rollback, a real queue, a migrated schema. The behavioral specs flag many of these as integration-tier; confirm against what the repo actually supports.

3. **Write the runnable-now tests** into the repository's conventional locations, in its style and framework, implementing each spec's `test_shape`, `expected_result`, and `evidence_required`. Write both the positive and negative cases. Do not weaken a test to make it pass; a test that should fail on bad code must fail on bad code.

4. **Write the needs-infrastructure tests too, but guard them** — mark them skipped/pending in the framework's idiomatic way, with a one-line comment naming exactly what infrastructure they need to run. They belong in the suite as a visible next step, not as silent failures.

5. **Run the suite** (or the relevant subset) using the repo's own test command. Capture pass/fail for the runnable-now tests and skipped status for the others.

6. **Report honestly.** Do not present a needs-infrastructure test as passing. Do not present a test you weakened as proof of anything.

## Output handling

Write the test files into the repository's test directories. Write a short report to the path given in the prompt (if none is given, ask). The report lists, per behavioral eval: its id, the test file written, and the result — passed, failed, or skipped-needs-infrastructure (with what it needs).

Print a short summary to chat: how many tests written, how many passed, how many failed, how many skipped for infrastructure, and the test command used. If anything failed, say what and why — a failing test on existing code is a real finding, not noise to hide.

## What this skill must not do

- Do not fake a pass. A test that cannot run is reported as skipped, never green.
- Do not weaken an assertion to get green. The negative cases exist to fail on bad code.
- Do not stand up new infrastructure (databases, queues) on its own. If a test needs it, it says so and leaves it for a human to decide.
