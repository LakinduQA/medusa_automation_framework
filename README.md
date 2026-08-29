# Medusa Automation Framework

A Playwright and pytest foundation for testing Medusa.js storefront, Admin, and API workflows.

## Features

- Python `src` package layout with environment-driven configuration
- Synchronous Playwright browser automation using a Page Object Model
- Reusable pytest fixtures for application context, browser pages, authentication, and API clients
- Medusa v2 clients for auth, products, carts, checkout, payment setup, orders, and regions
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

Requirements: Python 3.11 or newer and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run playwright install chromium
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
