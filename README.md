# Medusa Automation Framework

A Playwright and pytest foundation for testing Medusa.js storefront, Admin, and API workflows.

## Features

- Python `src` package layout with environment-driven configuration
- Synchronous Playwright browser automation using a Page Object Model
- Reusable pytest fixtures for application context, browser pages, authentication, and API clients
- Medusa v2 clients for auth, products, carts, checkout, payment setup, orders, and regions
- Portable Allure 3 reports with failure-only Playwright screenshots and traces
- Registered `smoke` and `e2e` pytest markers
- Repository-scoped agent skills for assessing, authoring, reviewing, and repairing tests
- GitHub Actions syntax validation on Linux and Windows

Browser flows are currently scaffolded; finalized test cases have not been added yet. Page Object locators may require tuning for the target storefront.

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

Check test discovery with:

```bash
uv run pytest --collect-only -q
```

Run quick checks or live end-to-end tests with:

```bash
uv run pytest -m smoke
uv run pytest -m e2e
```

Set `RUN_E2E=true` and provide the required application services, test data, credentials, and browser before running authenticated live flows.

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
| `PRODUCT_PATH_TEMPLATE` | Storefront product-detail route template |
| `CART_PATH` | Storefront cart route |
| `CHECKOUT_PATH` | Storefront checkout route |
| `STORE_API_PATH` | Store API root path |
| `ADMIN_API_PATH` | Admin API root path |
| `PUBLISHABLE_API_KEY` | Publishable key automatically sent to Store API routes |
| `ADMIN_EMAIL` | Admin username for authenticated flows |
| `ADMIN_PASSWORD` | Admin password for authenticated flows |
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
