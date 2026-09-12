from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest
from playwright.sync_api import Error, Page, expect

from medusa_automation.config import AppConfig
from medusa_automation.flows import StorefrontFlow
from medusa_automation.pages import (
    AccountPage,
    CartPage,
    CatalogPage,
    CheckoutPage,
    CustomerLoginPage,
    OrderConfirmationPage,
    ProductPage,
)
from medusa_automation.test_data import StorefrontTestData


@pytest.fixture(scope="session")
def storefront_test_data() -> StorefrontTestData:
    return StorefrontTestData.from_env()


@pytest.fixture
def require_test_data(
    storefront_test_data: StorefrontTestData,
) -> Callable[..., StorefrontTestData]:
    def require(*names: str) -> StorefrontTestData:
        missing = storefront_test_data.missing(*names)
        if missing:
            variables = ", ".join(f"TEST_{name.upper()}" for name in missing)
            pytest.skip(f"Storefront test data is not configured: {variables}")
        return storefront_test_data

    return require


@pytest.fixture
def live_storefront_enabled(run_live_tests: bool) -> None:
    if not run_live_tests:
        pytest.skip("Set RUN_E2E=true to run live storefront tests.")


@pytest.fixture
def storefront_page(
    live_storefront_enabled: None, page: Page, app_config: AppConfig
) -> Iterator[Page]:

    target = app_config.storefront_url(app_config.storefront_home_path)
    try:
        response = page.goto(target, wait_until="domcontentloaded")
    except Error as exc:
        pytest.skip(f"Storefront is unavailable at {target}: {exc}")

    if response is not None and response.status >= 400:
        pytest.skip(f"Storefront preflight returned HTTP {response.status} at {target}")

    expect(page.locator("body")).not_to_be_empty(timeout=app_config.timeout_ms)
    body = page.locator("body").inner_text().lower()
    if "welcome to medusa" in body and "sign in to access the account area" in body:
        pytest.skip(
            "STOREFRONT_URL resolves to Medusa Admin. Configure the customer storefront URL instead."
        )
    yield page


@pytest.fixture
def customer_login_page(
    storefront_page: Page, app_config: AppConfig
) -> CustomerLoginPage:
    return CustomerLoginPage(storefront_page, app_config)


@pytest.fixture
def account_page(storefront_page: Page, app_config: AppConfig) -> AccountPage:
    return AccountPage(storefront_page, app_config)


@pytest.fixture
def catalog_page(storefront_page: Page, app_config: AppConfig) -> CatalogPage:
    return CatalogPage(storefront_page, app_config)


@pytest.fixture
def storefront_product_page(
    storefront_page: Page, app_config: AppConfig
) -> ProductPage:
    return ProductPage(storefront_page, app_config)


@pytest.fixture
def storefront_cart_page(storefront_page: Page, app_config: AppConfig) -> CartPage:
    return CartPage(storefront_page, app_config)


@pytest.fixture
def storefront_checkout_page(
    storefront_page: Page, app_config: AppConfig
) -> CheckoutPage:
    return CheckoutPage(storefront_page, app_config)


@pytest.fixture
def order_confirmation_page(
    storefront_page: Page, app_config: AppConfig
) -> OrderConfirmationPage:
    return OrderConfirmationPage(storefront_page, app_config)


@pytest.fixture
def storefront_flow(
    storefront_page: Page,
    app_config: AppConfig,
    storefront_test_data: StorefrontTestData,
) -> StorefrontFlow:
    return StorefrontFlow(storefront_page, app_config, storefront_test_data)


@pytest.fixture
def authenticated_customer_page(
    storefront_page: Page,
    app_config: AppConfig,
    require_test_data: Callable[..., StorefrontTestData],
) -> Page:
    data = require_test_data("customer_email", "customer_password")
    login = CustomerLoginPage(storefront_page, app_config)
    login.open()
    login.login(data.customer_email, data.customer_password)
    AccountPage(storefront_page, app_config).assert_loaded()
    return storefront_page
