# Medusa Test Automation Skills

This directory contains repository-scoped instructions that help a compatible coding agent work consistently with this Medusa test framework.

## What a skill is

A skill is a directory whose `SKILL.md` file contains:

- YAML frontmatter with a unique `name` and a short `description`;
- instructions that are loaded only when the skill is selected;
- optional assets, such as the failure fixer's RCA template.

When an agent opens this repository, it discovers skills under `.agents/skills/`. It first sees each skill's name and description. For an implicit invocation, the agent compares the user's request with those descriptions and loads the best match. For an explicit invocation, the user names the skill with `$skill-name`.

Automatic selection is convenient for ordinary requests. Explicit invocation is useful when you want predictable routing or when a prompt could reasonably mean more than one thing.

## Skills and boundaries

| Skill | Use it when | Result | It does not |
|---|---|---|---|
| `medusa-test-case-assessor` | One case or a workbook/batch needs feasibility and completeness analysis | One verdict and recommendation per case, with batch reconciliation and consolidation guidance where applicable | Write or edit tests |
| `medusa-test-author` | One case or an assessed batch is approved or sufficiently complete | Traceable pytest/Playwright code, consolidated where appropriate, and targeted validation | Guess through material gaps or repair an unrelated failure |
| `medusa-test-reviewer` | Existing code must be compared with one or more source cases | Severity-ranked findings, source-ID reconciliation, coverage mapping, and verdict | Edit files unless explicitly requested |
| `medusa-test-failure-fixer` | A specific test is failing and needs diagnosis and repair | Evidence-backed RCA, smallest safe local fix, and verification | Hide product/environment defects or run the whole suite as a general service |

The boundaries prevent similar prompts from activating the wrong workflow. For example, "Can this test be automated?" is assessment, while "Implement this approved test" is authoring. "Review this test" does not authorize edits, while "Fix this failing test" does.

## Recommended workflow

```text
Raw test case
    |
    v
Test-case assessor
    |-- blocked ----------------> clarify requirements or restore dependencies
    |-- conditionally feasible -> satisfy named conditions
    `-- feasible
          |
          v
      Test author
          |
          v
      Test reviewer
          |-- findings ---------> explicitly request corrections, then review again
          `-- pass
                |
                v
            Run the test
                |-- passes -----> done
                `-- fails ------> failure fixer -> RCA -> targeted verification
```

Not every request needs the complete sequence. The reviewer can inspect code written by a human, and the failure fixer can investigate an existing failing test even when the other skills were not used. The important gate is that authoring should start from a sufficiently complete case.

## Automatic invocation examples

These prompts should cause the agent to select one skill from the request's meaning:

```text
Assess whether this checkout test case is automatable and identify missing test data.
```

Expected skill: `medusa-test-case-assessor`

```text
Assess every case in this workbook, identify consolidation opportunities, and reconcile the totals. Do not write tests.
```

Expected skill: `medusa-test-case-assessor` (batch result)

```text
Implement this approved cart test as a Playwright pytest test.
```

Expected skill: `medusa-test-author`

```text
Compare tests/test_checkout.py with test case TC-42 and report false-positive risks.
```

Expected skill: `medusa-test-reviewer`

```text
Fix tests/test_checkout.py::test_places_order and document the root cause.
```

Expected skill: `medusa-test-failure-fixer`

A request such as "run the entire browser matrix" should not select these skills. A future suite-runner skill can cover that responsibility once the repository's browser matrix, reporting, and CI commands are finalized.

## Explicit invocation examples

Prefix the request with the exact skill name:

```text
$medusa-test-case-assessor Assess TC-42 from the steps below.
```

```text
$medusa-test-author Implement the approved TC-42 assessment.
```

```text
$medusa-test-reviewer Review TC-42 against tests/test_checkout.py. Do not edit.
```

```text
$medusa-test-failure-fixer Fix tests/test_checkout.py::test_places_order.
```

Explicit selection chooses the workflow, but it does not broaden permissions. A skill still cannot commit, push, expose secrets, mutate unrelated external systems, or expand the requested test scope.

## How the skills use the framework

- The assessor inspects configuration, fixtures, API clients, Page Objects, existing tests, and environment dependencies before deciding feasibility. For batches, it also returns one row per case, recommendation and verdict totals, consolidation groups, partial/manual boundaries, and source-quality findings.
- The author reuses the same framework layers and adds the smallest test-specific code required.
- The reviewer traces each source test-case step through the test and its dependencies.
- The failure fixer reproduces one target, uses framework artifacts as evidence, and writes a tracked report under `docs/test-rca/`.

The fixer copies `medusa-test-failure-fixer/assets/rca-template.md` for each investigation. Private learning notes are ignored separately, so RCA reports remain eligible for source control.

## Validation

The skill-creator validator requires PyYAML. Run it without modifying the project environment:

```powershell
$validator = "C:\Users\<you>\.codex\skills\.system\skill-creator\scripts\quick_validate.py"
uv run --isolated --no-project --with pyyaml python $validator .agents/skills/medusa-test-case-assessor
uv run --isolated --no-project --with pyyaml python $validator .agents/skills/medusa-test-author
uv run --isolated --no-project --with pyyaml python $validator .agents/skills/medusa-test-reviewer
uv run --isolated --no-project --with pyyaml python $validator .agents/skills/medusa-test-failure-fixer
```

`--isolated` creates a temporary environment, `--no-project` prevents installation of this repository, and `--with pyyaml` adds only the validator's missing dependency to that temporary environment.
