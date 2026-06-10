---
name: judge-validation-runner
description: Validate an LLM-as-judge rubric against recent real commits so its verdicts can be trusted.
---

# Judge Validation Runner

## Purpose

A judge rubric is a candidate standard until you have measured it against reality. This skill measures it: it runs one rubric against the repository's recent real commits, presents each commit with the judge's verdict and the evidence it cited, and lets a human confirm or override each call. From those rulings it computes how often the judge agreed with the human and turns every disagreement into a specific rubric fix.

The human ruling is the ground truth. The judge's verdict is the thing being tested. The report must therefore make it easy to *disagree* — it shows the diff and the judge's cited evidence and asks the human to rule, rather than leading with the judge's verdict as if it were the answer. Validating a judge means checking it, not rubber-stamping it.

This uses real commits, not invented ones: a fabricated diff tests the judge against a guess about what real code looks like, which defeats the purpose. Recent real history is the sample.

## Two modes

**harvest** — pull the recent commits touching the rubric's surface, run the judge on each, save the results, then walk the human through them one commit at a time in the conversation to collect confirm/override rulings.

**score** — read the saved rulings back, compute agreement, and produce the rubric-fix list.

Detect the mode from the prompt. If not stated: if no saved results with rulings exist, run **harvest**; if they exist, run **score**.

## Inputs

- Rubric file: the path given in the prompt (the output of the judge-rubric-designer skill). If no path is given, ask for one. Rubric selection: the rubric id(s) named in the prompt — one or more (e.g. `J01`, or `J01 J02 J03`). If none are named, default to every `block`-severity rubric in the file, since those gate merges and are the validate-first set. `all` selects every rubric regardless of severity.
- Assertions file: the path given in the prompt (the output of the codebase-assertion-designer skill). If no path is given, ask for one. Used to resolve the rubric's `source_signals` to the assertion's `files_or_patterns_to_inspect` — that is the *surface* used to filter commits.
- Time window: the prompt's window, else the last 30 days.
- Results file: the path given in the prompt. In harvest mode the judge results and rulings are saved here; in score mode they are read back from here. If no path is given, ask for one.

If the rubric or assertions file is missing, say so and stop.

## harvest mode

Run this for each selected rubric. Each rubric has its own surface, its own qualifying commits, and its own section in the report.

### Phase A — harvest and save (silent)

1. Resolve the surface for the rubric: from its `source_signals`, look up each assertion's `files_or_patterns_to_inspect` in the assertions file. That set of files/paths is the surface. Different rubrics resolve to different surfaces, so a commit may qualify for one rubric and not another.
2. `git log --since="<window>"` and filter to commits whose diff touches that rubric's surface. Use `git show <sha>` to get each commit's diff.
3. For each qualifying commit, run the judge: evaluate that commit's diff against the rubric's `grading_criteria`, producing a binary verdict (`pass` or `block`) and citing the specific lines per the rubric's `must_cite`. Follow the rubric's `model_guidance` for which model acts as judge. (The model executing this skill is acting as the judge here; in production it is a separate controlled call.)
4. Save all results to the file (see format).

Do this phase silently. Do not print the verdicts, the per-commit reasoning, a tally, or any preview to the conversation. The only thing to print before the walkthrough is one line: how many commits qualified, and the small-sample caveat if fewer than 6.

### Phase B — walkthrough, strictly one commit at a time

Present exactly ONE commit, then STOP and wait for the human's ruling. Do not show the next commit, a list of remaining commits, a tally, or a preview of what's coming. Do not predict how the human will rule. Do not editorialize ("the one that matters," "textbook example," "your move") — no framing, no labels, no commentary.

For the single commit on screen, show only:
- the commit subject
- the surface-relevant diff hunks
- the verdict (`pass` or `block`) and a one-line rationale
- the prompt: "Confirm or override? (say 'why' for the judge's full reasoning)"

Then stop. On the human's response:
- if they say "why" (or similar), show that commit's full reasoning and any out-of-surface ground-truth note, then ask for the ruling again
- record their ruling (`confirm`, or `override` + corrected verdict + one-line reason) into the saved file
- only then present the next single commit, the same way

The human may stop at any point; rulings so far are saved. When several rubrics are validated together, walk `block`-severity rubrics first.

## score mode

Run this per rubric section in the report, producing one result block per rubric.

1. Read the saved results. For each commit under each rubric, read the human's recorded ruling (`confirm` or `override`) and reason. Commits the human did not rule on are simply not counted.
2. Agreement = confirms / total rulings, computed per rubric. Report each rubric's agreement alongside its commit count, repeating the small-sample caveat where it applied.
3. Split each rubric's overrides into the two error types, because they matter differently:
   - **judge passed, human blocked** = a missed failure. The expensive error. For a `block`-severity rubric, prioritize eliminating these (favor recall).
   - **judge blocked, human passed** = a false alarm. Cheaper — costs a human a look.
4. For each override, map the human's reason to the specific `grading_criteria` line(s) of that rubric to tighten or loosen. This is the per-rubric fix list.
5. Do not auto-edit any rubric. Present the fix lists and let the human decide; a validation run proposes rubric changes, it does not silently make them.

## Output handling

Save the results to the path given in the prompt, creating any parent directory it names. The walkthrough records each ruling into this file as it is given, so progress survives if the human stops partway. In score mode, append the agreement summary and fix list to the same file, preserving the saved rulings.

After either mode, print a short summary to chat: mode, the rubric id(s) validated, window, and commits qualified per rubric — and in score mode, each rubric's agreement figure and the count of each override type.

## Saved results format (harvest writes this; score reads it)

Save structured per-commit records so the walkthrough and score mode share one source of truth. Keep the human-facing default (subject, diff, verdict, one-line rationale) separate from the on-request detail (full reasoning, cited evidence, ground-truth notes) so the walkthrough can show the former and reveal the latter only when asked.

```yaml
window: <window>
rubrics_validated: [<ids>]
judge_note: "Model executing the skill applied each rubric's criteria. Binary verdict. In production the judge is a separate controlled call."
results:
  - rubric_id:
    dimension:
    severity:
    commits_qualifying:
    surface: [<files/paths>]
    small_sample: <true|false>     # true if commits_qualifying < 6
    commits:
      - sha:
        subject:
        surface_diff:              # the surface-relevant hunks (shown by default)
        verdict:                   # pass | block
        rationale:                 # one line (shown by default)
        full_reasoning:            # cited evidence + criteria applied (shown only on request)
        ground_truth_note:         # any out-of-surface fact the scoped judge could not see
        ruling:                    # confirm | override | null (unrules)
        corrected_verdict:         # set only if ruling == override
        ruling_reason:             # one line, set only if ruling == override
```

## Walkthrough behavior (harvest)

For each commit, show the subject, the `surface_diff`, and the `verdict` + `rationale`. Ask for a ruling. If the human says "why" (or similar), show `full_reasoning` and `ground_truth_note`, then ask again. Record `ruling` (and `corrected_verdict` / `ruling_reason` on override) into the saved file before moving on. The human may stop at any point.

## Score summary (score mode appends this)

One result block per rubric.

```markdown
# Validation Result — <window>

## <rubric id>
Commits ruled: <N>   Agreement: <confirms>/<N>
<small-sample caveat if it applied>

Missed failures (judge pass, human block): <count>
False alarms (judge block, human pass): <count>

### Rubric fix list — <rubric id>
- criterion <which>: <tighten/loosen, based on override reason>
```
