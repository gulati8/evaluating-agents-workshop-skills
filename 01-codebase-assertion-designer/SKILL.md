---
name: codebase-assertion-designer
description: Read a repository and write down its conventions, each with the assertion an agent must keep true when it changes code here, as a machine-readable file and a review form the team corrects.
---

# Codebase Assertion Designer

## Purpose

Read a repository and write down its **conventions**, so that an agent changing code here follows them and a reviewer can check that it did.

Two outputs, same content:

1. `conventions.json`: the machine-readable version. Later steps use it to check whether a change kept every assertion true.
2. `conventions.html`: a review form. The team keeps, fixes, or drops each convention. Their corrections are what the conventions become.

You are proposing. The team decides. Write every convention so it is easy to disagree with: show where you saw it, show where the repo breaks it, say how sure you are.

## Vocabulary

Four words, used only as defined here:

- **candidate**: a pattern you have noticed in the repo but not yet tested.
- **convention**: a candidate that has passed the four tests below.
- **assertion**: what must be true for the convention to hold, in one plain sentence.
- **mechanism**: how this repo keeps the assertion true today: the helpers, paths, and shapes involved.

Every entry in the output is a convention. Every convention has exactly one assertion and one mechanism.

## The four tests

A candidate becomes a convention only if it passes all four:

1. **An agent could plausibly break it** while doing ordinary work in this repo.
2. **An agent would not already know it.** It is specific to this repo, not standard practice any capable model does by default.
3. **A reviewer would send the change back** if it were broken. Not mention it. Send it back.
4. **It recurs.** The pattern appears in more than one place. If it happens once, it is not a pattern.

If any test fails, the candidate is dropped. Most candidates fail one of them. That is expected.

### Examples

**Passes all four.**

> Assertion: Anything read or written under `/organizations/:orgId` is scoped to that org in the query.
> Mechanism: `request.params.orgId` goes into the Prisma `where`, directly or through the owning relation.

An agent adding a new endpoint could easily forget it. Nothing about the framework implies it. A reviewer would block the change.

**Fails test 3. Housekeeping.**

> Put one-off working files in `tmp/` and durable scripts in `packages/backend/scripts/`.

An agent might break it, but no reviewer sends a change back over it.

**Fails test 2. Standard practice.**

> Construct third-party SDK clients lazily on first use, not at module load.

A reviewer would send it back, but any capable agent does this by default. Writing it down adds nothing.

**Fails test 3. Taste.**

> Write a comment only for an invariant the code cannot express.

Two reviewers would disagree on whether it was broken.

**A bundle that must be split.** This was proposed as one candidate:

> When you add a background job: declare its Queue and a typed JobData interface in `src/lib/queues.ts` and append it to `allQueues`; register a Worker with explicit `concurrency` in `src/worker.ts` and add it to `workerQueuePairs`; payloads carry ids only; custom jobIds must contain no `:`.

It is four candidates. Tested separately:

- Every queue and its worker are registered in both lists, so failures route to the dead-letter queue. **Convention.** Easy to miss, repo-specific, reviewer blocks it.
- Job payloads carry ids only; handlers re-read the row. **Convention.** Separate assertion, separate reason.
- Workers set explicit concurrency. **Fails test 3.** A reviewer would mention it, not block.
- Job ids cannot contain a colon. **Fails test 2 in reverse:** it is a library gotcha, not a convention of this repo.

One assertion per convention. If the sentence has "and" joining two things a reviewer could judge separately, it is two candidates.

## Process

1. Survey the repository. Learn the stack, the major layers, and where each kind of code lives from the directory layout and the code itself. Read only code. Do not read documentation of any kind: no README, no contributing guide, no architecture or design docs, no glossary. Documentation says what the repo claims; you are recording what it does. Do not list every file; that costs context and tells you little.
   Then split the reading by area: one subagent per area, each reading in its own context and returning only its candidates with evidence, compactly. Merge in the main session. This is the default. If the prompt says `single-reader`, do all the reading in the main session instead.
2. Read enough real code in each layer to see the patterns. Several files per pattern, not one. A candidate seen once is a guess.
3. Grep for conformance. Reading is expensive and grep is cheap: once you have a candidate, search the whole tree for where it holds and where it breaks. Counter-examples are what let the team decide whether it is a convention or an accident.
4. Look hardest at the surfaces where a silent mistake costs the most: authorization, data and schema, API contracts, background work, error handling, tests. Take structure and style candidates only where they are clearly deliberate.
5. Apply the four tests to every candidate. Drop what fails. What remains are the conventions.
6. A convention has two parts. Write each as its own field: the **assertion**, what must be true, and the **mechanism**, how this repo keeps it true today. Never put both in one sentence. People correct the assertion. The mechanism is there so they can check it.
7. Decide how a change could be checked against each assertion:
   - `reading`: a mechanical check on the diff can tell. Files changed, symbols present, things that changed together.
   - `test`: only running the code can tell. Say what a test would prove.
   - `judgment`: it needs a reader to reason about the change. State the question a reviewer would ask.
8. Rate confidence in each convention: `high` if it holds across the repo with no counter-examples, `medium` if it holds mostly, `low` if you saw it but are not sure it is deliberate.
9. Order the conventions by the cost of breaking them, highest first, so a reader who stops early has seen what matters.
10. Write the JSON file, then render the form.

## Evidence

Every convention cites at least one real source file, with an excerpt copied verbatim. Evidence is code that keeps the assertion true. Documentation is never evidence.

## Inputs and outputs

This skill reads the repository in the working directory. It takes no input file.

Write both outputs to the output directory given in the prompt, creating it if needed. If no output directory is given, use `./assertion-designer` in the repository root.

1. Write `<output dir>/conventions.json` in the format below.
2. Render the form by running, from the directory this skill lives in:

   ```
   python3 render_form.py <output dir>/conventions.json <output dir>/conventions.html
   ```

   The script uses only the Python standard library. If it fails, report the error. Do not hand-write the HTML instead.

After writing, print a short summary to the conversation: the repo name, the number of conventions, the count by `check` and by `confidence`, and both paths written. Do not paste the JSON into chat.

## Output format

Write this structure exactly to `conventions.json`:

```json
{
  "repo": "name of the repository",
  "generated_at": "ISO-8601 timestamp",
  "profile": {
    "stack": "one line: languages, frameworks, build tool",
    "layers": ["one line per major layer and where it lives"],
    "tests": "one line: framework, location, how they run",
    "notes": ["anything else a reviewer should know before reading the conventions"]
  },
  "conventions": [
    {
      "id": "C01",
      "assertion": "One plain sentence: what must be true.",
      "mechanism": "How this repo makes it true today: the helpers, paths, and shapes involved.",
      "category": "authorization | data | api | jobs | errors | observability | testing | dependencies | structure | style",
      "confidence": "high | medium | low",
      "why_it_matters": "One sentence: what goes wrong when the assertion is false.",
      "evidence": [
        { "path": "relative/path/to/file.ext", "excerpt": "a few lines, verbatim" }
      ],
      "counter_examples": [
        { "path": "relative/path/to/file.ext", "note": "how the assertion is false here" }
      ],
      "check": "reading | test | judgment",
      "check_detail": "For reading: what a mechanical check looks for in a diff. For test: what a test would prove. For judgment: the question a reviewer answers."
    }
  ]
}
```

`counter_examples` may be an empty list. Nothing else may be omitted.
