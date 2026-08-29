---
name: medusa-test-reviewer
description: Review an existing Medusa pytest/Playwright test against its supplied test case for coverage, assertion quality, false positives, resilience, isolation, dependencies, secrets, and Page Object conventions. Use for review findings, not implementation or failure repair, and do not edit unless explicitly asked.
---

# Medusa Test Reviewer

Compare the supplied test case with the existing test implementation and produce evidence-based review findings. This is a review workflow: do not edit files unless the user explicitly asks for changes.

## Gather evidence

Read the complete test case, the test file, imported fixtures and helpers, relevant Page Objects and API clients, `conftest.py`, `pyproject.toml`, `.env.example`, and related tests. Use line-specific references for findings. Collection or other read-only diagnostics are appropriate when useful; do not run live, externally mutating tests merely to perform a review unless the user asks.

## Review criteria

Map each test-case step and expected result to the implementation. Check for:

- omitted, reordered, substituted, or extra behavior that changes the case's meaning;
- missing, weak, tautological, or unrelated assertions and paths that could pass without proving the expected outcome;
- assertions made before state settles, swallowed exceptions, unconditional branches, or setup that pre-satisfies the result;
- locator resilience, strictness, scoping, and use of accessible roles, labels, stable test IDs, and Page Object boundaries;
- raw sleeps, arbitrary retries, timing assumptions, or network-idle assumptions that hide synchronization problems;
- isolation, deterministic data, uniqueness, cleanup, idempotence, and dependence on execution order;
- authentication, region, inventory, shipping, payment, browser, service, and environment dependencies;
- hard-coded or exposed credentials, keys, tokens, personal data, or sensitive output;
- appropriate fixture and API-client reuse, synchronous Playwright conventions, and registered `smoke` or `e2e` markers;
- whether API setup or verification accidentally bypasses the UI behavior the case is meant to prove.

Do not recommend weakening an expected result just to match the current script.

## Rank findings

Report actionable findings first, ordered by severity:

- `critical`: exposes secrets, causes destructive unintended effects, or makes the test fundamentally unsafe.
- `high`: can falsely pass/fail or omits a core requirement.
- `medium`: creates meaningful fragility, coupling, or maintainability risk.
- `low`: a localized improvement with limited behavioral risk.

For each finding, include the severity, file and line, affected test-case step, evidence, impact, and a concrete correction. Do not manufacture findings to fill severity levels.

Then provide:

1. a step-to-code coverage table, including each expected result;
2. assumptions or evidence gaps that limited the review;
3. a concise overall verdict: `pass`, `pass with minor findings`, or `changes required`.

If there are no findings, say so explicitly and mention any residual validation gap. Do not commit, push, change external systems, or expand the requested review scope.
