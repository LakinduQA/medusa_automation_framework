from __future__ import annotations

from collections.abc import Iterator

import pytest
from playwright.sync_api import Page

from medusa_automation.fixtures.app import TestContext
from medusa_automation.pages import CartPage, CheckoutPage, LoginPage, ProductPage


@pytest.fixture
def login_page(page: Page, app_config) -> LoginPage:
    return LoginPage(page, app_config)


@pytest.fixture
def product_page(page: Page, app_config) -> ProductPage:
    return ProductPage(page, app_config)


@pytest.fixture
def cart_page(page: Page, app_config) -> CartPage:
    return CartPage(page, app_config)


@pytest.fixture
def checkout_page(page: Page, app_config) -> CheckoutPage:
    return CheckoutPage(page, app_config)


@pytest.fixture
def authenticated_page(page: Page, live_test_context: TestContext, run_live_tests: bool) -> Iterator[Page]:
    if not run_live_tests:
        pytest.skip("Set RUN_E2E=true to use authenticated browser flows.")
    if live_test_context.admin_credentials is None:
        pytest.skip("Set ADMIN_EMAIL and ADMIN_PASSWORD for authenticated browser flows.")

    login = LoginPage(page, live_test_context.config)
    login.open()
    login.login(live_test_context.admin_credentials.email, live_test_context.admin_credentials.password)
    yield page
