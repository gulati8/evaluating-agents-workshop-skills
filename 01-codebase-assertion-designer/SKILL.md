---
name: codebase-assertion-designer
description: Read a repository and write down its conventions, the rules for how code in this repo should be written, as a machine-readable file and a review form the team corrects.
---

# Codebase Assertion Designer

## Purpose

Read a repository and write down its **conventions**: the rules for how code in this repository is written. Not generic best practices. The rules this repo actually follows, stated so that someone writing new code here (a person or an agent) would know what to do.

Two outputs, same content:

1. `conventions.json`: the machine-readable version. Later steps use it to check whether a change kept every assertion true.
2. `conventions.html`: a review form. The team keeps, fixes, or drops each convention. Their corrections are what the conventions become.

You are proposing. The team decides. Write every convention so it is easy to disagree with: show where you saw it, show where the repo breaks it, say how sure you are.

## When to use this skill

Use when asked to:

- write down a repository's conventions or coding rules
- produce the assertions about how code in a repo should be written
- profile how a codebase is actually built, for a team to review
- prepare the first layer of an agent-code evaluation loop

## The four tests

A convention should be captured for review only if it passes all four:

1. **An agent could plausibly break it** while doing ordinary work in this repo.
2. **An agent would not already know it.** It is specific to this repo, not standard practice that is known from training.
3. **A reviewer would send the change back** if it were broken. Not mention it. Send it back.
4. **It recurs.** The pattern appears in more than one place. If it happens once, it is not a pattern.

If any test fails, the candidate is dropped. Most candidates fail one of them. That is expected.

### Examples

**Passes all four.**

> Assertion: Anything read or written under `/organizations/:orgId` should be scoped to that org in the query.
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

1. Read the repository structure. Identify the stack, the major layers, and where each kind of code lives.
2. Read enough real code in each layer to see the patterns. Read several files per pattern, not one. A single occurrence is not a convention. Read code only, do not infer convention from documentation, only from the code itself. If you cannot find a pattern, do not invent one.
3. For each pattern, look for counter-examples. If a convention is not followed in the repo, say where. The team needs that to decide whether it should be enforced.
4. Look specifically at these surfaces, because they are where a silent mistake costs the most, but do not limit the rules to them:
   - authorization, permissions, access control
   - data access, schema, migrations, transactions
   - API surface, contracts, request and response shapes
   - error handling and what is allowed to fail silently
   - logging, audit, metrics
   - tests: where they live, how they are named, what they set up, what they assert
   - dependencies, build, and configuration
   - repository structure: what goes where, what must change together
5. Write each convention as an instruction addressed to the writer. "Every route handler calls the auth helper before reading data" is a convention. "Auth helper is present in route files" is a diff check. Write the first kind.
6. For each convention, decide how a change could be checked against it:
   - `reading`: a mechanical check on the diff can tell. Which files changed, what symbols appear, what changed together.
   - `test`: only running the code can tell. Describe what a test would prove.
   - `judgment`: it needs a reader to reason about the change. State the question a reviewer would ask.
7. Rate your confidence in each convention: `high` if it holds across the repo with no counter-examples, `medium` if it holds mostly, `low` if you saw it but are not sure it is deliberate.
8. Write the JSON file, then render the form.

## Evidence

- **Address the writer.** Every convention should complete the sentence "when you write code in this repo, ...".
- **Name real things.** Real paths, real helpers, real directories from this repo. A convention that could be true of any codebase is not a convention of this one.
- **One assertion per entry.** Do not bundle. A convention can be verified through a single assertion, if multiple are required, it is multiple conventions.
- **Show your evidence.** At least one real file path and a short excerpt per convention. If you cannot cite it, do not propose it.
- **Show the breaks.** If the repo violates the convention anywhere, list where. Never hide a counter-example to make a convention look cleaner.
- **Say what it protects.** One sentence on what goes wrong when the convention is broken. If nothing goes wrong, the convention is probably style, and should say so in its category.
- **Do not pad.** Twenty rules the team argues about beat sixty they skim. Aim for the conventions that matter most on the surfaces in step 4, then add structure and style rules only where they are clearly deliberate.

## Inputs and outputs

This skill reads the repository in the working directory. It takes no input file.

Write both outputs to the output directory given in the prompt, creating it if needed. If no output directory is given, use `./tmp/assertion-designer` in the repository root.

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
      "convention": "The instruction, addressed to the writer, naming real things in this repo.",
      "mechanism": "How this repo makes it true today: the helpers, paths, and shapes involved.",
      "category": "authorization | data | api | jobs | errors | observability | testing | dependencies | structure | style",
      "confidence": "high | medium | low",
      "why_it_matters": "One sentence: what goes wrong when the instruction is not followed.",
      "evidence": [
        { "path": "relative/path/to/file.ext", "excerpt": "a few lines, verbatim" }
      ],
      "counter_examples": [
        { "path": "relative/path/to/file.ext", "note": "how the convention is violated here" }
      ],
      "check": "reading | test | judgment",
      "check_detail": "For reading: what a mechanical check looks for in a diff. For test: what a test would prove. For judgment: the question a reviewer answers."
    }
  ]
}
```

`counter_examples` may be an empty list. Nothing else may be omitted.
