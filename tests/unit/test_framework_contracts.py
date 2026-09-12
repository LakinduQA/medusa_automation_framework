from __future__ import annotations

from unittest.mock import Mock

from medusa_automation.api import BaseApiClient, CartApiClient, CheckoutApiClient
from medusa_automation.case_registry import (
    ALL_SOURCE_CASE_IDS,
    AUTOMATED_SOURCE_CASE_IDS,
    BLOCKED_SOURCE_CASE_IDS,
)
from medusa_automation.config import AppConfig
from medusa_automation.test_data import StorefrontTestData


def test_source_case_registry_reconciles_portfolio() -> None:
    assert len(ALL_SOURCE_CASE_IDS) == 90
    assert len(AUTOMATED_SOURCE_CASE_IDS) == 89
    assert BLOCKED_SOURCE_CASE_IDS == {"TC-PS-005"}
    assert AUTOMATED_SOURCE_CASE_IDS | BLOCKED_SOURCE_CASE_IDS == set(
        ALL_SOURCE_CASE_IDS
    )


def test_config_keeps_admin_storefront_and_api_urls_separate(monkeypatch) -> None:
    monkeypatch.setenv("BACKEND_URL", "http://backend.example")
    monkeypatch.setenv("STOREFRONT_URL", "http://storefront.example")
    monkeypatch.setenv("ADMIN_URL", "http://admin.example")
    config = AppConfig.from_env()

    assert config.storefront_url("/account") == "http://storefront.example/account"
    assert config.admin_url("/app") == "http://admin.example/app"
    assert config.store_api_url("/products") == "http://backend.example/store/products"
    assert config.admin_api_url("/products") == "http://backend.example/admin/products"


def test_storefront_test_data_reports_only_missing_requested_values(
    monkeypatch,
) -> None:
    monkeypatch.setenv("TEST_PRODUCT_NAME", "Medusa T-Shirt")
    monkeypatch.delenv("TEST_PRODUCT_HANDLE", raising=False)
    data = StorefrontTestData.from_env()

    assert data.product_name == "Medusa T-Shirt"
    assert data.missing("product_name", "product_handle") == ["product_handle"]


def test_store_request_adds_publishable_key_without_overwriting_headers() -> None:
    request_context = Mock()
    request_context.fetch.return_value = Mock()
    client = BaseApiClient(
        AppConfig(
            backend_base_url="http://backend.example",
            publishable_api_key="pk_test",
        ),
        request_context,
    )

    client.get("/products", headers={"x-test": "value"})

    request_context.fetch.assert_called_once_with(
        "http://backend.example/store/products",
        method="GET",
        timeout=15_000,
        headers={"x-test": "value", "x-publishable-api-key": "pk_test"},
    )


def test_cart_line_item_update_uses_medusa_v2_post_contract() -> None:
    request_context = Mock()
    request_context.fetch.return_value = Mock()
    client = CartApiClient(
        AppConfig(backend_base_url="http://backend.example"), request_context
    )

    client.update_line_item("cart_1", "item_1", quantity=2)

    request_context.fetch.assert_called_once_with(
        "http://backend.example/store/carts/cart_1/line-items/item_1",
        method="POST",
        timeout=15_000,
        json={"quantity": 2},
    )


def test_shipping_options_use_cart_query_parameter() -> None:
    request_context = Mock()
    request_context.fetch.return_value = Mock()
    client = CheckoutApiClient(
        AppConfig(backend_base_url="http://backend.example"), request_context
    )

    client.list_shipping_options("cart_1")

    request_context.fetch.assert_called_once_with(
        "http://backend.example/store/shipping-options",
        method="GET",
        timeout=15_000,
        params={"cart_id": "cart_1"},
    )
