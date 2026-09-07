from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from medusa_automation.pages import CartPage, ProductPage
from tests.support import case

pytestmark = [pytest.mark.e2e]


@pytest.mark.source_case("TC-PD-001")
def test_product_details_show_required_information(
    storefront_product_page: ProductPage, require_test_data
) -> None:
    data = require_test_data("product_handle")
    storefront_product_page.open_product(data.product_handle)
    storefront_product_page.assert_required_details()


@pytest.mark.parametrize(
    ("_case_id", "option_attr", "values_attr"),
    [
        case(
            "TC-PD-002",
            "TC-PD-002",
            "color_option_name",
            ("primary_color", "secondary_color"),
        ),
        case(
            "TC-PD-003",
            "TC-PD-003",
            "size_option_name",
            ("primary_size", "secondary_size"),
        ),
    ],
)
def test_product_option_selection_is_visible_and_retained(
    _case_id: str,
    option_attr: str,
    values_attr: tuple[str, str],
    storefront_product_page: ProductPage,
    require_test_data,
) -> None:
    data = require_test_data("product_handle", option_attr, *values_attr)
    storefront_product_page.open_product(data.product_handle)
    for value_attr in values_attr:
        storefront_product_page.select_option(
            getattr(data, option_attr), getattr(data, value_attr)
        )


@pytest.mark.source_case("TC-PD-004")
def test_selected_variant_is_retained_in_cart(
    storefront_flow, require_test_data
) -> None:
    data = require_test_data(
        "product_handle", "product_name", "primary_color", "primary_size"
    )
    cart = storefront_flow.add_default_product()
    cart.assert_item_details(data.product_name, data.primary_color, data.primary_size)


@pytest.mark.parametrize(
    ("_case_id", "selected_option", "selected_value", "missing_label"),
    [
        case("TC-PD-005", "TC-PD-005", "Size", "M", "colour"),
        case("TC-PD-006", "TC-PD-006", "Color", "Black", "size"),
    ],
)
def test_required_variant_option_omission_prevents_add_to_cart(
    _case_id: str,
    selected_option: str,
    selected_value: str,
    missing_label: str,
    storefront_product_page: ProductPage,
    storefront_cart_page: CartPage,
    require_test_data,
) -> None:
    data = require_test_data("product_handle", "product_name")
    storefront_product_page.open_product(data.product_handle)
    storefront_product_page.select_option(selected_option, selected_value)
    if storefront_product_page.add_to_cart_button.is_enabled():
        storefront_product_page.add_to_cart()
        expect(
            storefront_product_page.page.get_by_text(
                re.compile(
                    rf"select.*{missing_label}|{missing_label}.*required", re.IGNORECASE
                )
            ).first
        ).to_be_visible()
    else:
        expect(storefront_product_page.add_to_cart_button).to_be_disabled()
    storefront_cart_page.open()
    storefront_cart_page.assert_item_removed(data.product_name)


@pytest.mark.source_case("TC-PD-007")
def test_invalid_variant_combination_cannot_be_added(
    storefront_product_page: ProductPage, require_test_data
) -> None:
    data = require_test_data("unavailable_combination_product_handle")
    storefront_product_page.open_product(data.unavailable_combination_product_handle)
    storefront_product_page.select_option(data.color_option_name, data.primary_color)
    storefront_product_page.select_option(data.size_option_name, data.secondary_size)
    storefront_product_page.assert_add_to_cart_unavailable()


@pytest.mark.parametrize(
    "_case_id",
    [
        case("TC-PD-008", "TC-PD-008"),
        case("TC-PD-013", "TC-PD-013"),
    ],
)
def test_out_of_stock_variant_is_identified_and_not_purchasable(
    _case_id: str, storefront_product_page: ProductPage, require_test_data
) -> None:
    data = require_test_data("out_of_stock_product_handle")
    storefront_product_page.open_product(data.out_of_stock_product_handle)
    expect(
        storefront_product_page.page.get_by_text(
            re.compile(r"out of stock", re.IGNORECASE)
        ).first
    ).to_be_visible()
    storefront_product_page.assert_add_to_cart_unavailable()


@pytest.mark.source_case("TC-PD-009")
@pytest.mark.partial
def test_configured_related_products_are_displayed(
    storefront_product_page: ProductPage, require_test_data
) -> None:
    data = require_test_data("product_handle", "related_product_name")
    storefront_product_page.open_product(data.product_handle)
    expect(
        storefront_product_page.related_products()
        .filter(has_text=data.related_product_name)
        .first
    ).to_be_visible()


@pytest.mark.source_case("TC-PD-010")
def test_related_product_opens_matching_details(
    storefront_product_page: ProductPage, require_test_data
) -> None:
    data = require_test_data("product_handle", "related_product_name")
    storefront_product_page.open_product(data.product_handle)
    storefront_product_page.related_products().filter(
        has_text=data.related_product_name
    ).get_by_role("link").first.click()
    storefront_product_page.assert_product_heading(data.related_product_name)


@pytest.mark.source_case("TC-PD-011")
def test_product_without_related_items_remains_functional(
    storefront_product_page: ProductPage, require_test_data
) -> None:
    data = require_test_data("no_related_product_handle")
    storefront_product_page.open_product(data.no_related_product_handle)
    storefront_product_page.assert_product_heading()
    related_heading = storefront_product_page.page.get_by_role(
        "heading", name=re.compile(r"related products", re.IGNORECASE)
    )
    assert (
        related_heading.count() == 0
        or storefront_product_page.related_products().count() == 0
    )
    expect(storefront_product_page.page.get_by_role("alert")).to_have_count(0)


@pytest.mark.source_case("TC-PD-012")
def test_add_to_cart_updates_cart_count(storefront_flow, require_test_data) -> None:
    require_test_data("product_handle", "product_name")
    product = storefront_flow.open_product()
    storefront_flow.select_default_variant(product)
    before = product.cart_count().inner_text() if product.cart_count().count() else "0"
    product.add_to_cart()
    expect(product.cart_count()).not_to_have_text(before)


@pytest.mark.source_case("TC-PD-014")
def test_requested_quantity_cannot_exceed_inventory(
    storefront_product_page: ProductPage,
    storefront_cart_page: CartPage,
    require_test_data,
) -> None:
    data = require_test_data(
        "limited_stock_product_handle", "limited_stock_product_name", "inventory_limit"
    )
    limit = int(data.inventory_limit)
    storefront_product_page.open_product(data.limited_stock_product_handle)
    storefront_product_page.set_quantity(limit + 1)
    storefront_product_page.add_to_cart()
    expect(
        storefront_product_page.page.get_by_role("alert")
        .or_(
            storefront_product_page.page.get_by_text(
                re.compile(r"inventory|stock|available quantity", re.IGNORECASE)
            )
        )
        .first
    ).to_be_visible()
    storefront_cart_page.open()
    if storefront_cart_page.line_item(data.limited_stock_product_name).count():
        assert (
            storefront_cart_page.quantity_value(data.limited_stock_product_name)
            <= limit
        )


@pytest.mark.source_case("TC-PD-015")
@pytest.mark.resilience
def test_add_to_cart_failure_recovers_without_duplicate_item(
    storefront_product_page: ProductPage,
    storefront_cart_page: CartPage,
    storefront_flow,
    require_test_data,
) -> None:
    data = require_test_data("product_handle", "product_name")
    pattern = re.compile(r"/store/carts/.*/line-items")
    storefront_product_page.page.route(
        pattern,
        lambda route: route.fulfill(
            status=500, json={"message": "Controlled add-to-cart failure"}
        ),
        times=1,
    )
    storefront_product_page.open_product(data.product_handle)
    storefront_flow.select_default_variant(storefront_product_page)
    storefront_product_page.add_to_cart()
    expect(storefront_product_page.add_to_cart_button).not_to_have_text(
        re.compile(r"loading", re.IGNORECASE),
        timeout=storefront_product_page.config.timeout_ms,
    )
    expect(
        storefront_product_page.page.get_by_role("alert")
        .or_(
            storefront_product_page.page.get_by_text(
                re.compile(r"error|failed|try again", re.IGNORECASE)
            )
        )
        .first
    ).to_be_visible()
    storefront_cart_page.open()
    storefront_cart_page.assert_item_removed(data.product_name)
