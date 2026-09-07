---
name: medusa-test-case-assessor
description: Assess one or more supplied Medusa pytest/Playwright test cases for automation feasibility and completeness before implementation, including portfolio-level batch analysis. Use for test-case assessment, not for writing, reviewing, or fixing test code.
---

# Medusa Test Case Assessor

Assess whether each supplied test case can be automated faithfully in this repository. A request may contain one case or a workbook/batch. Do not create or edit test code.

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

For a workbook or batch, also assess the portfolio for:

- automation value and risk coverage relative to implementation and maintenance cost;
- requirement, UI, data, and environment stability;
- determinism, observability, controllability, repeatability, and isolation;
- exact duplicates, overlapping scenarios, and parameterization opportunities;
- cases that should be partially automated with an explicit manual complement;
- contradictory, shifted, copied, blank, or otherwise unreliable source results;
- a sensible regression wave or priority for implementation.

Preserve the supplied source unless the user explicitly requests edits. Report source-data defects rather than silently correcting them.

Choose the automation layer based on what the case proves:

- Use UI automation when the behavior under test is rendering, navigation, accessibility, or user interaction.
- Use API automation when the contract, status, or backend state is the behavior under test.
- Use a hybrid approach when APIs can create or inspect state while the UI remains the behavior being proved. Do not replace a required UI assertion with an API assertion merely because it is easier.

## Verdict

Return exactly one verdict per supplied case:

- `feasible`: the case has enough information and repository support to implement without material assumptions.
- `conditionally feasible`: implementation is credible, but named assumptions, configuration, test data, or minor clarifications must be satisfied.
- `blocked`: faithful automation depends on missing acceptance criteria, unavailable capabilities or services, missing authorization or credentials, or another issue that prevents a meaningful test.

Treat absent secrets and unavailable external services as prerequisites or blockers, never as permission to invent values or mutate an external system. If only a small ambiguity exists, state a conservative assumption and use `conditionally feasible`; do not block unnecessarily.

For a batch, give each case a separate feasibility verdict and a separate automation recommendation. Recommendations should distinguish independent automation, consolidation/parameterization, partial automation with retained manual coverage, and cases that should not be automated as written. Reconcile verdict and recommendation totals to the source-case count so no case is silently omitted or counted twice. Cross-reference every consolidation group and every partial-automation case.

## Response format

For a single case, provide:

1. **Verdict** and a short rationale.
2. **Step and assertion coverage**, mapping each case step to the observable check and noting gaps.
3. **Prerequisites and test data**, including authentication, environment, payment, and shipping needs.
4. **Recommended approach**: UI, API, or hybrid, with a concise implementation outline and likely reusable fixtures, clients, and Page Objects.
5. **Conditions or blockers**, with the specific information or capability needed to resolve each one.
6. **Readiness**, stating whether the case is ready for `medusa-test-author`.

For a workbook or batch, provide:

1. **Scope and reconciliation**, including source row count, unique case count, duplicates or identifier issues, verdict totals, and recommendation totals.
2. **Portfolio findings**, covering ROI, risk, stability, determinism, observability, controllability, duplication, maintenance cost, environment support, and manual complements.
3. **Case matrix**, with one row per source case containing ID, module, recommendation, feasibility verdict, UI/API/hybrid layer, regression wave, engineering rationale, prerequisites, missing capability or clarification, and consolidation target.
4. **Consolidation map**, listing every grouped source ID and the proposed maintainable automation target.
5. **Partial-automation boundary**, stating the deterministic checks to automate and the judgment, device, browser, visual, or assistive-technology checks that remain manual.
6. **Readiness and next actions**, naming the conditions that must be satisfied before cases move to `medusa-test-author`.

Do not write tests, add Page Object methods, change configuration, commit, push, or change external systems while assessing.
