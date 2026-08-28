from __future__ import annotations

from collections.abc import Iterator

import pytest
from playwright.sync_api import APIRequestContext, Playwright

from medusa_automation.api import (
    AuthApiClient,
    BaseApiClient,
    CartApiClient,
    CheckoutApiClient,
    OrdersApiClient,
    ProductsApiClient,
    RegionsApiClient,
)


@pytest.fixture
def api_request_context(playwright: Playwright, app_config) -> Iterator[APIRequestContext]:
    context = playwright.request.new_context(
        base_url=app_config.backend_base_url or app_config.base_url,
        timeout=app_config.timeout_ms,
        ignore_https_errors=app_config.ignore_https_errors,
        storage_state=app_config.storage_state_path,
    )
    try:
        yield context
    finally:
        context.dispose()


@pytest.fixture
def base_api_client(app_config, api_request_context: APIRequestContext) -> BaseApiClient:
    return BaseApiClient(config=app_config, request_context=api_request_context)


@pytest.fixture
def auth_api_client(app_config, api_request_context: APIRequestContext) -> AuthApiClient:
    return AuthApiClient(config=app_config, request_context=api_request_context)


@pytest.fixture
def products_api_client(app_config, api_request_context: APIRequestContext) -> ProductsApiClient:
    return ProductsApiClient(config=app_config, request_context=api_request_context)


@pytest.fixture
def cart_api_client(app_config, api_request_context: APIRequestContext) -> CartApiClient:
    return CartApiClient(config=app_config, request_context=api_request_context)


@pytest.fixture
def checkout_api_client(app_config, api_request_context: APIRequestContext) -> CheckoutApiClient:
    return CheckoutApiClient(config=app_config, request_context=api_request_context)


@pytest.fixture
def orders_api_client(app_config, api_request_context: APIRequestContext) -> OrdersApiClient:
    return OrdersApiClient(config=app_config, request_context=api_request_context)


@pytest.fixture
def regions_api_client(app_config, api_request_context: APIRequestContext) -> RegionsApiClient:
    return RegionsApiClient(config=app_config, request_context=api_request_context)
