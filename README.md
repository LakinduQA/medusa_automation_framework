# Medusa Automation Framework

A base Playwright + pytest automation framework for Medusa.js applications.

## What is included

- `src`-based Python package layout
- Page Object Model structure with:
  - `BasePage`
  - `LoginPage`
  - `ProductPage`
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
2. Install the project dependencies.
3. Copy `.env.example` to `.env` and update values.

## Environment variables

- `BASE_URL` - application URL under test
- `ADMIN_LOGIN_PATH` - login page path
- `PRODUCTS_PATH` - product catalog path
- `PRODUCT_PATH_TEMPLATE` - product detail URL template
- `STORE_API_PATH` - store API root path
- `ADMIN_API_PATH` - admin API root path
- `ADMIN_EMAIL` - admin username for authenticated flows
- `ADMIN_PASSWORD` - admin password for authenticated flows
- `HEADLESS` - run browsers headless by default
- `SLOW_MO` - optional Playwright delay in milliseconds

## Framework modules

- Browser flows are scaffolded only; no finalized test cases are included yet.
- API clients currently cover the main Medusa flows: auth, products, carts, checkout, orders, and regions.
