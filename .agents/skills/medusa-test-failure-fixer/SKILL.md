---
name: medusa-test-failure-fixer
description: Diagnose and repair a specific failing Medusa pytest/Playwright test, recording evidence and verification in a tracked RCA report. Use when a test is failing and a root-cause fix is requested, not for new test authoring, feasibility assessment, review-only work, or general suite execution.
---

# Medusa Test Failure Fixer

Reproduce a specific failing test, preserve the evidence in a tracked RCA, determine the root cause, apply the smallest safe repository-local fix when one exists, and verify the result.

## Scope and safety

Obtain the test node ID and the command or failure output from the request or repository evidence. Narrow a file-level failure to a specific node when possible. Do not broaden into a suite-wide repair without a separate request.

Never make a test pass by weakening a valid assertion, deleting coverage, swallowing an exception, adding arbitrary waits, increasing retries without evidence, or marking the test skipped or expected-failing. Do not commit, push, expose secrets, or change external systems. Product defects, missing credentials, unavailable services, invalid external data, and unsupported environments are blockers unless a safe repository-local correction is genuinely the cause.

## Create the RCA

At the first reproduction attempt, copy `assets/rca-template.md` to:

```text
docs/test-rca/YYYY-MM-DD-<sanitized-test-node-id>.md
```

Use the local date. Sanitize the node ID by converting path separators, `::`, whitespace, and characters outside letters, digits, `.`, `_`, and `-` to hyphens; collapse repeated hyphens, trim punctuation, and use lowercase. Keep the useful test identity and shorten an excessive name deterministically. If the path already belongs to a different investigation, add a short deterministic suffix rather than overwriting it.

Update the RCA throughout the work. Record concise evidence and artifact paths, not secrets or large raw logs. Use repository-relative paths when possible.

## Diagnose

1. Inspect the test case if available, the failing test, fixtures, Page Objects, API clients, configuration, and recent relevant code.
2. Run the exact targeted test once to reproduce, preserving the command, exit result, failure signature, and paths to available logs, screenshots, videos, or traces.
3. Compare the failure with the intended assertion and separate symptoms from cause. Classify the root cause as `test code`, `fixture/framework`, `product defect`, `test data/dependency`, `environment/configuration`, `flaky/timing`, or `unknown`.
4. State confidence and evidence. Record plausible rejected hypotheses and why the evidence does not support them.
5. Define the smallest solution and affected files before editing.

If reproduction is impossible, use supplied artifacts and static evidence, clearly lower the confidence, and document the missing prerequisite. Do not invent a runtime diagnosis.

## Fix and verify

When evidence supports a safe repository-local fix, implement it automatically and keep it limited to the diagnosed cause. Prefer condition-based Playwright synchronization, resilient locators, deterministic setup, and correct fixture or client behavior.

Rerun the exact target after the change. Run the narrowest relevant supporting check when the fix touches shared framework code. If flakiness is suspected, perform a bounded verification of exactly three consecutive targeted runs; report each result and stop after the third rather than retrying until green. A mixed result is not a pass.

When the cause is a product defect or external/environment blocker, do not disguise it as a test fix. Leave code unchanged unless a separate safe repository defect is also demonstrated, and complete the RCA with the blocker and the action needed from the owning system or user.

Finish the RCA with implemented changes, commands and results, remaining risks or blockers, and final status: `fixed`, `blocked`, or `unresolved`. In the response, link the RCA, summarize the root cause and change, and distinguish verified results from unrun checks.
