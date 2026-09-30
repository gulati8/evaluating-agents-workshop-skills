---
name: codebase-assertion-designer
description: Read a repository and write down its conventions, the rules for how code in this repo should be written, as a machine-readable file and a review form the team corrects.
---

# Codebase Assertion Designer

## Purpose

Read a repository and write down its **conventions**: the rules for how code in this repository is written. Not generic best practice. The rules this repo actually follows, stated so that someone writing new code here (a person or an agent) would know what to do.

Two outputs, same content:

1. `conventions.json`: the machine-readable version. Later steps read this to check whether a change followed the rules.
2. `conventions.html`: a review form. The team reads each rule, keeps it, fixes it, or drops it. Their corrections are what the rules become.

You are proposing. The team decides. Write every rule so that it is easy to disagree with: say where you saw it, say where the repo breaks it, and say how sure you are.

## When to use this skill

Use when asked to:

- write down a repository's conventions or coding rules
- produce the assertions about how code in a repo should be written
- profile how a codebase is actually built, for a team to review
- prepare the first layer of an agent-code evaluation loop

Work from the repository as it is. No feature request or task is needed.

## Process

1. Read the repository structure. Identify the stack, the major layers, and where each kind of code lives.
2. Read enough real code in each layer to see the patterns. Read several files per pattern, not one. A rule seen once is a guess, not a convention.
3. For each pattern, look for counter-examples. If a rule is broken in the repo, say where. The team needs that to decide whether it is a rule or an accident.
4. Look specifically at these surfaces, because they are where a silent mistake costs the most, but do not limit the rules to them:
   - authorization, permissions, access control
   - data access, schema, migrations, transactions
   - API surface, contracts, request and response shapes
   - error handling and what is allowed to fail silently
   - logging, audit, metrics
   - tests: where they live, how they are named, what they set up, what they assert
   - dependencies, build, and configuration
   - repository structure: what goes where, what must change together
5. Write each convention as a rule addressed to the writer. "Every route handler calls the auth helper before reading data" is a rule. "Auth helper is present in route files" is a diff check. Write the first kind.
6. For each rule, decide how a change could be checked against it:
   - `reading`: a mechanical check on the diff can tell. Which files changed, what symbols appear, what changed together.
   - `test`: only running the code can tell. Describe what a test would prove.
   - `judgment`: it needs a reader to reason about the change. State the question a reviewer would ask.
7. Rate your confidence in each rule: `high` if it holds across the repo with no counter-examples, `medium` if it holds mostly, `low` if you saw it but are not sure it is deliberate.
8. Write the JSON file, then render the form.

## Rules for writing rules

- **Address the writer.** Every rule should complete the sentence "when you write code in this repo, ...".
- **Name real things.** Real paths, real helpers, real directories from this repo. A rule that could be true of any codebase is not a convention of this one.
- **One rule per entry.** Do not bundle. A rule the team can only half-agree with is two rules.
- **Show your evidence.** At least one real file path and a short excerpt per rule. If you cannot cite it, do not propose it.
- **Show the breaks.** If the repo violates the rule anywhere, list where. Never hide a counter-example to make a rule look cleaner.
- **Say what it protects.** One sentence on what goes wrong when the rule is broken. If nothing goes wrong, the rule is probably style, and should say so in its category.
- **Do not pad.** Twenty rules the team argues about beat sixty they skim. Aim for the rules that matter most on the surfaces in step 4, then add structure and style rules only where they are clearly deliberate.

## Inputs and outputs

This skill reads the repository in the working directory. It takes no input file.

Write both outputs to the output directory given in the prompt, creating it if needed. If no output directory is given, use `./workshop-out` in the repository root.

1. Write `<output dir>/conventions.json` in the format below.
2. Render the form by running, from the directory this skill lives in:

   ```
   python3 render_form.py <output dir>/conventions.json <output dir>/conventions.html
   ```

   The script uses only the Python standard library. If it fails, report the error. Do not hand-write the HTML instead.

After writing, print a short summary to the conversation: the repo name, the number of rules, the count by `check` (reading / test / judgment), the count by `confidence`, and both paths written. Do not paste the JSON into chat.

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
    "notes": ["anything else a reviewer should know before reading the rules"]
  },
  "conventions": [
    {
      "id": "C01",
      "rule": "The rule, addressed to the writer, naming real things in this repo.",
      "category": "authorization | data | api | errors | observability | testing | dependencies | structure | style",
      "confidence": "high | medium | low",
      "why_it_matters": "One sentence: what goes wrong when this is broken.",
      "evidence": [
        { "path": "relative/path/to/file.ext", "excerpt": "a few lines showing the rule followed" }
      ],
      "counter_examples": [
        { "path": "relative/path/to/file.ext", "note": "how it breaks the rule here" }
      ],
      "check": "reading | test | judgment",
      "check_detail": "For reading: what a mechanical check looks for in a diff. For test: what a test would prove, and how. For judgment: the question a reviewer answers."
    }
  ]
}
```

`counter_examples` may be an empty list. Nothing else may be omitted.
