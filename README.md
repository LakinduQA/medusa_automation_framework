# Medusa Automation Framework

A Playwright and pytest foundation for testing Medusa.js storefront, Admin, and API workflows.

## Features

- Python `src` package layout with environment-driven configuration
- Synchronous Playwright browser automation using a Page Object Model
- Reusable pytest fixtures for application context, browser pages, authentication, and API clients
- Medusa v2 clients for auth, products, carts, checkout, payment setup, orders, and regions
- Portable Allure 3 reports with failure-only Playwright screenshots and traces
- Registered `smoke` and `e2e` pytest markers
- 89 traceable storefront cases covering login, listing, product details, cart, and checkout
- Collection-time reconciliation against the 90-case source portfolio
- Repository-scoped agent skills for assessing, authoring, reviewing, and repairing tests
- GitHub Actions syntax validation on Linux and Windows

The source portfolio contains 90 unique cases. Eighty-nine are implemented; `TC-PS-005` remains intentionally blocked because its multi-filter AND/OR rule has no approved expected behavior. Twelve cases automate their deterministic portion and retain the manual visual, true-Safari/device, or assistive-technology checks identified in the feasibility assessment.

## Project structure

```text
.
|-- .agents/skills/                 Repository-scoped test automation skills
|-- .github/workflows/ci.yml        CI syntax validation
|-- src/medusa_automation/
|   |-- api/                        Reusable Medusa API clients
|   |-- fixtures/                   Shared pytest fixtures
|   |-- pages/                      Playwright Page Objects
|   `-- config.py                   Environment-backed configuration
|-- tests/                          Source-case-aligned storefront suite
|-- conftest.py                     Fixture plugin registration and src-path setup
|-- pyproject.toml                  Package, dependency, and pytest configuration
`-- .env.example                    Local configuration template
```

## Setup with uv

Requirements: Python 3.11 or newer, [uv](https://docs.astral.sh/uv/), and Node.js 22 or newer for report generation.

```bash
uv sync
uv run playwright install chromium
npm ci
```

Copy `.env.example` to `.env`, then update the URLs, credentials, and keys required by the environment under test. The `.env` file is ignored by Git.

## Seed the local Medusa data

For the Medusa 2.16 backend currently running on port 9000, this repository includes a safe coordinator for the backend's native seed and an idempotent test-customer setup. It creates the standard published catalog, regions, EUR/USD pricing, stock, shipping options, a publishable key when one is missing, and the isolated customer used by the UI suite. It does not use SQL or delete existing data.

1. Copy [`.env.example`](.env.example) to `.env`, then copy the values from [`test-data/storefront-default-seed.env`](test-data/storefront-default-seed.env) into it. Set a unique `TEST_CUSTOMER_PASSWORD` and, if required by your store, `PUBLISHABLE_API_KEY`.
2. Confirm the backend is stopped or points to a disposable development database. The upstream native seed is intended for a fresh database; it creates catalog and fulfillment records and is not a reset command.
3. From this framework directory, run:

```powershell
.\scripts\seed-storefront-default-data.ps1
```

If the backend is elsewhere, pass its absolute location:

```powershell
.\scripts\seed-storefront-default-data.ps1 -BackendPath 'D:\path\to\my-medusa-store'
```

The script verifies an existing test customer without changing it; otherwise it registers and creates that customer. To seed only the backend catalog and skip customer creation, use `-SkipCustomer`.

The default Medusa seed is a baseline, not a complete UI fixture pack: it does not create the controlled out-of-stock, limited-stock, unavailable-variant, session-expiry, or payment-disruption hooks required by the resilience cases. Leave those `TEST_*` values blank until the customer storefront exposes approved, deterministic controls. Do not invent expected totals or bypass those cases; their preflight will identify missing data rather than report false application failures.

Check test discovery with:

```bash
uv run pytest --collect-only -q
```

Run quick checks or live end-to-end tests with:

```bash
uv run pytest -m smoke
uv run pytest -m e2e
```

Set `RUN_E2E=true` and provide the required customer storefront, test data, credentials, and browser before running live flows. `http://localhost:9000/app` is the Medusa Admin surface; it is not a valid `STOREFRONT_URL` for these customer-facing cases. The storefront preflight skips with an explicit prerequisite reason when the storefront is offline or resolves to Admin.

Each implemented source ID is attached through `pytest.mark.source_case`. Collection fails if an approved case is missing, duplicated, unknown, or if the blocked case is accidentally implemented:

```bash
uv run pytest --collect-only -q
```

## Test reports

Every pytest run writes Allure result data to `allure-results/`, JUnit XML to `test-results/junit.xml`, and Playwright artifacts to `test-results/`. Failed browser tests automatically retain a full-page screenshot and a Playwright trace; passing tests do not retain browser evidence.

Generate the portable Allure 3 report after a run:

```bash
npm run report:generate
```

Open `allure-report/index.html` directly in a browser. The report is a single HTML file containing the test results and failure attachments. Opening a trace from the report loads the viewer from `trace.playwright.dev`; if that site is unavailable, open the downloaded `trace.zip` locally instead:

```bash
uv run playwright show-trace path/to/trace.zip
```

GitHub Actions uses the same commands and uploads the HTML report, JUnit XML, raw Allure results, and failure artifacts for each operating-system/Python matrix job. Until finalized tests are added, the workflow treats pytest's `no tests collected` result as an intentional skip; collection and configuration errors still fail CI.

## Environment variables

| Variable | Purpose |
|---|---|
| `BASE_URL` | Fallback URL when a more specific URL is not configured |
| `BACKEND_URL` | Medusa backend URL used by Store, Admin, and Auth APIs |
| `STOREFRONT_URL` | Storefront URL used by product, cart, and checkout pages |
| `ADMIN_URL` | Medusa Admin URL used by browser-based admin pages |
| `ADMIN_LOGIN_PATH` | Admin login route |
| `PRODUCTS_PATH` | Admin product catalog route |
| `STOREFONT_HOME_PATH` | Customer storefront health-check route |
| `CUSTOMER_LOGIN_PATH` | Customer login route |
| `CUSTOMER_ACCOUNT_PATH` | Protected customer account route |
| `PRODUCT_LISTING_PATH` | Customer product-listing route |
| `PRODUCT_PATH_TEMPLATE` | Storefront product-detail route template |
| `CART_PATH` | Storefront cart route |
| `CHECKOUT_PATH` | Storefront checkout route |
| `STORE_API_PATH` | Store API root path |
| `ADMIN_API_PATH` | Admin API root path |
| `PUBLISHABLE_API_KEY` | Publishable key automatically sent to Store API routes |
| `ADMIN_EMAIL` | Admin username for authenticated flows |
| `ADMIN_PASSWORD` | Admin password for authenticated flows |
| `TEST_CUSTOMER_EMAIL`, `TEST_CUSTOMER_PASSWORD` | Registered, isolated customer credentials |
| `TEST_PRODUCT_HANDLE`, `TEST_PRODUCT_NAME` | Default purchasable product identity |
| `TEST_*_PRODUCT_HANDLE` | Controlled no-related, out-of-stock, limited-stock, and unavailable-combination products |
| `TEST_FILTER_*`, `TEST_LATEST_PRODUCT_NAME` | Deterministic listing filter and sort oracles |
| `TEST_*_SHIPPING`, `TEST_MANUAL_PAYMENT` | Configured delivery and payment names |
| `TEST_EXPECTED_*` | Currency-safe cart and checkout total oracles |
| `TEST_INVENTORY_*_ENDPOINT` | Approved inventory mutation and restoration endpoints for `TC-CART-012` |
| `TEST_SESSION_EXPIRY_ENDPOINT` | Approved server-side session invalidation hook |
| `TEST_PAYMENT_FAILURE_PATTERN`, `TEST_PAYMENT_CANCEL_LABEL` | Controlled payment disruption and cancellation hooks |
| `TEST_PAYMENT_SENSITIVE_SENTINEL` | Test-only payment value that must never render after submission |
| `HEADLESS` | Intended browser headless setting |
| `SLOW_MO` | Intended Playwright action delay in milliseconds |
| `BROWSER` | Intended browser selection; defaults to Chromium |
| `TIMEOUT_MS` | Default Page Object and API request timeout |
| `STORAGE_STATE_PATH` | Optional Playwright authentication state file |
| `IGNORE_HTTPS_ERRORS` | Allow invalid certificates when explicitly enabled |
| `RUN_E2E` | Enables live or authenticated end-to-end flows |

## Agent-assisted test workflow

Compatible agents discover the skills under `.agents/skills/` when working in this repository. They can select a skill automatically from the request or the user can invoke one explicitly:

- `$medusa-test-case-assessor` checks whether a test case is complete and feasible.
- `$medusa-test-author` implements an approved test case.
- `$medusa-test-reviewer` compares an existing test with its source test case.
- `$medusa-test-failure-fixer` diagnoses a failing test, records an RCA, and applies a safe local fix when appropriate.

The normal sequence is assess, author, review, and then use the failure fixer only when an implemented test fails. See [.agents/skills/README.md](.agents/skills/README.md) for invocation examples, boundaries, and the complete workflow.
