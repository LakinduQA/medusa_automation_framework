# Medusa Automation Framework

A base Playwright + pytest automation framework for Medusa.js applications.

## What is included

- `src`-based Python package layout
- Page Object Model structure with:
  - `BasePage`
  - `LoginPage`
  - `ProductPage`
  - `CartPage`
  - `CheckoutPage`
- Separate fixture modules under `src/medusa_automation/fixtures/`
- API client layer under `src/medusa_automation/api/` using Playwright `APIRequestContext`
- Environment-based configuration
- GitHub Actions CI workflow

## Project structure

- `src/medusa_automation/config.py` - environment-driven test configuration
- `src/medusa_automation/pages/` - page objects
- `src/medusa_automation/api/` - reusable API clients
- `src/medusa_automation/fixtures/` - shared pytest fixtures
- `conftest.py` - pytest plugin registration and source-path setup

## Setup

1. Create and activate a Python environment.
2. Install the project dependencies with `pip install -e .`.
3. Copy `.env.example` to `.env` and update values.

## Environment variables

- `BASE_URL` - fallback URL used when a more specific URL is not configured
- `BACKEND_URL` - Medusa backend URL used for Store, Admin, and Auth APIs
- `STOREFRONT_URL` - storefront URL used by product, cart, and checkout pages
- `ADMIN_URL` - Medusa Admin URL used by admin browser pages
- `ADMIN_LOGIN_PATH` - login page path
- `PRODUCTS_PATH` - product catalog path
- `PRODUCT_PATH_TEMPLATE` - product detail URL template
- `CART_PATH` - storefront cart path
- `CHECKOUT_PATH` - storefront checkout path
- `STORE_API_PATH` - store API root path
- `ADMIN_API_PATH` - admin API root path
- `PUBLISHABLE_API_KEY` - Medusa publishable API key sent to Store API routes
- `ADMIN_EMAIL` - admin username for authenticated flows
- `ADMIN_PASSWORD` - admin password for authenticated flows
- `HEADLESS` - run browsers headless by default
- `SLOW_MO` - optional Playwright delay in milliseconds
- `TIMEOUT_MS` - default API and page-operation timeout
- `STORAGE_STATE_PATH` - optional Playwright authentication state file
- `IGNORE_HTTPS_ERRORS` - allow invalid HTTPS certificates when explicitly enabled

## Framework modules

- Browser flows are scaffolded only; no finalized test cases are included yet.
- Cart and checkout Page Objects provide reusable semantic actions but may need locator tuning for a specific storefront design.
- Medusa v2 API clients cover auth, products, carts, checkout, payment setup, orders, and regions.
- Store API calls automatically include `PUBLISHABLE_API_KEY` when configured.
