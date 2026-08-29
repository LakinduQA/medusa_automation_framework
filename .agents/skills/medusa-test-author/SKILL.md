---
name: medusa-test-author
description: Implement an approved or sufficiently complete Medusa test case as pytest/Playwright code in this repository. Use for authoring tests and only the necessary supporting Page Object or fixture changes, not for feasibility assessment, review-only requests, or failure repair.
---

# Medusa Test Author

Turn a supplied, approved or sufficiently complete test case into focused pytest/Playwright code that follows this repository's conventions.

## Confirm the implementation basis

Read the complete test case and any assessment. If an assessment is `blocked`, do not implement until the blocker is resolved. For a `conditionally feasible` case, implement only when the stated conditions are satisfied or the user accepts explicit, low-risk assumptions. If no assessment exists, confirm from the case itself that the actions, expected results, prerequisites, and test data are sufficiently defined; otherwise report the precise gaps without producing a speculative test.

Inspect `README.md`, `pyproject.toml`, `.env.example`, `conftest.py`, existing tests, and relevant code under:

- `src/medusa_automation/fixtures/`
- `src/medusa_automation/api/`
- `src/medusa_automation/pages/`

The repository uses synchronous Playwright, pytest fixtures registered through `conftest.py`, and strict `smoke` and `e2e` markers. Preserve those choices.

## Implement the narrow test

- Add tests under `tests/` using pytest discovery names.
- Map every test-case step to an action and every expected result to a meaningful assertion. Assert business outcomes or observable state, not merely that an action completed.
- Reuse `app_config`, browser/Page Object fixtures, and API client fixtures before adding new infrastructure.
- Reuse Page Object methods for UI behavior. Add or tune the smallest Page Object method needed when the behavior is missing; keep selectors and interaction details out of the test when they are reusable UI concerns.
- Prefer accessible roles, labels, stable test IDs, and scoped locators. Avoid positional selectors, broad text matches, brittle CSS/XPath tied to layout, and duplicated locator logic.
- Rely on Playwright auto-waiting and explicit state assertions. Never add raw sleeps or arbitrary delays.
- Use APIs for setup or cleanup when that preserves what the case is intended to prove. Do not turn a UI case into an API-only test.
- Keep tests independent and repeatable. Use unique data when collisions are possible and clean up state created by the test when a safe repository-supported mechanism exists.
- Read credentials and keys through existing configuration or fixtures. Never hard-code, log, snapshot, or commit secrets.
- Apply `pytest.mark.smoke` to genuinely quick, focused checks and `pytest.mark.e2e` to live end-to-end browser flows. Do not add unregistered markers.
- Preserve established live-environment gates such as `RUN_E2E`; do not add skips merely to avoid a failure.

Do not broaden the test case, refactor unrelated framework code, change external systems beyond the case's authorized test actions, or commit or push changes.

## Validate

Run the narrowest useful checks:

1. `uv run pytest --collect-only -q <test-file-or-node-id>`
2. `uv run pytest -q <test-node-id>` when the required application, data, browsers, configuration, and credentials are available
3. a relevant syntax or static check for any supporting files changed

Do not claim runtime success when a live dependency is unavailable. Report the exact command run, result, and any environment limitation. Summarize the files changed and how the implementation covers the original steps.
