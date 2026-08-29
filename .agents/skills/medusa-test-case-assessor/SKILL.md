---
name: medusa-test-case-assessor
description: Assess a supplied Medusa pytest/Playwright test case for feasibility and completeness before implementation, including prerequisites, data, authentication, dependencies, and UI versus API approach. Use for test-case assessment, not for writing, reviewing, or fixing test code.
---

# Medusa Test Case Assessor

Assess whether the supplied test case can be automated faithfully in this repository. Do not create or edit test code.

## Establish repository context

Read the test case and inspect the relevant repository files before deciding. At minimum, check `README.md`, `pyproject.toml`, `.env.example`, `conftest.py`, and the relevant modules under `src/medusa_automation/fixtures/`, `src/medusa_automation/api/`, and `src/medusa_automation/pages/`. Inspect existing tests when present.

Do not assume that a scaffolded Page Object matches the deployed storefront. Separate repository evidence from assumptions about the application or environment.

## Assess the case

Trace every stated action to an observable expected result. Identify:

- missing, ambiguous, contradictory, or untestable steps and assertions;
- starting state, cleanup needs, and whether the case can run independently and repeatedly;
- required products, variants, inventory, regions, currencies, customers, carts, orders, and unique data;
- authentication roles, session state, publishable keys, credentials, and other configuration;
- shipping options, payment providers, webhooks, third-party redirects, email, or other external dependencies;
- environment and browser assumptions, including whether a live storefront or backend must be running;
- destructive or externally mutating operations that require separate authorization.

Choose the automation layer based on what the case proves:

- Use UI automation when the behavior under test is rendering, navigation, accessibility, or user interaction.
- Use API automation when the contract, status, or backend state is the behavior under test.
- Use a hybrid approach when APIs can create or inspect state while the UI remains the behavior being proved. Do not replace a required UI assertion with an API assertion merely because it is easier.

## Verdict

Return exactly one verdict:

- `feasible`: the case has enough information and repository support to implement without material assumptions.
- `conditionally feasible`: implementation is credible, but named assumptions, configuration, test data, or minor clarifications must be satisfied.
- `blocked`: faithful automation depends on missing acceptance criteria, unavailable capabilities or services, missing authorization or credentials, or another issue that prevents a meaningful test.

Treat absent secrets and unavailable external services as prerequisites or blockers, never as permission to invent values or mutate an external system. If only a small ambiguity exists, state a conservative assumption and use `conditionally feasible`; do not block unnecessarily.

## Response format

Provide:

1. **Verdict** and a short rationale.
2. **Step and assertion coverage**, mapping each case step to the observable check and noting gaps.
3. **Prerequisites and test data**, including authentication, environment, payment, and shipping needs.
4. **Recommended approach**: UI, API, or hybrid, with a concise implementation outline and likely reusable fixtures, clients, and Page Objects.
5. **Conditions or blockers**, with the specific information or capability needed to resolve each one.
6. **Readiness**, stating whether the case is ready for `medusa-test-author`.

Do not write tests, add Page Object methods, change configuration, commit, push, or change external systems while assessing.
