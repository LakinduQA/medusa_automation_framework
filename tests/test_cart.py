from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from medusa_automation.pages import AccountPage, CartPage
from tests.support import (
    assert_keyboard_reachable,
    assert_no_horizontal_overflow,
    case,
    visible_controls,
)

pytestmark = [pytest.mark.e2e]


def prepared_cart(storefront_flow, require_test_data) -> tuple[CartPage, object]:
    data = require_test_data(
        "customer_email", "customer_password", "product_handle", "product_name"
    )
    storefront_flow.login()
    return storefront_flow.add_default_product(), data


@pytest.mark.source_case("TC-CART-001")
def test_cart_displays_added_product_details(
    storefront_flow, require_test_data
) -> None:
    cart, data = prepared_cart(storefront_flow, require_test_data)
    cart.assert_item_details(data.product_name, data.primary_color, data.primary_size)
    expect(cart.quantity_input(data.product_name)).to_have_value("1")


@pytest.mark.parametrize(
    ("_case_id", "start", "direction", "expected"),
    [
        case("TC-CART-002", "TC-CART-002", 1, "increase", 2),
        case("TC-CART-003", "TC-CART-003", 2, "decrease", 1),
    ],
)
def test_cart_quantity_change_recalculates_totals(
    _case_id: str,
    start: int,
    direction: str,
    expected: int,
    storefront_flow,
    require_test_data,
) -> None:
    cart, data = prepared_cart(storefront_flow, require_test_data)
    cart.update_quantity(data.product_name, start)
    before = cart.summary_amount("Subtotal")
    getattr(cart, f"{direction}_quantity")(data.product_name)
    expect(cart.quantity_input(data.product_name)).to_have_value(str(expected))
    after = cart.summary_amount("Subtotal")
    assert (after > before) if direction == "increase" else (after < before)


@pytest.mark.parametrize(
    "_case_id",
    [
        case("TC-CART-004", "TC-CART-004"),
        case("TC-CART-008", "TC-CART-008"),
    ],
)
def test_remove_item_updates_cart_state(
    _case_id: str, storefront_flow, require_test_data
) -> None:
    cart, data = prepared_cart(storefront_flow, require_test_data)
    cart.remove_item(data.product_name)
    cart.assert_item_removed(data.product_name)


@pytest.mark.parametrize(
    ("_case_id", "expected_amounts"),
    [
        case(
            "TC-CART-005",
            "TC-CART-005",
            {
                "Subtotal": "expected_subtotal_qty_2",
                "Shipping": "expected_shipping_qty_2",
                "Tax": "expected_tax_qty_2",
                "Total": "expected_total_qty_2",
            },
        ),
        case(
            "TC-CART-006",
            "TC-CART-006",
            {"Subtotal": "expected_subtotal_qty_2"},
        ),
        case(
            "TC-CART-007",
            "TC-CART-007",
            {
                "Subtotal": "expected_subtotal_qty_2",
                "Shipping": "expected_shipping_qty_2",
                "Tax": "expected_tax_qty_2",
                "Total": "expected_total_qty_2",
            },
        ),
    ],
)
def test_cart_summary_recalculates_after_quantity_change(
    _case_id: str,
    expected_amounts: dict[str, str],
    storefront_flow,
    require_test_data,
) -> None:
    cart, data = prepared_cart(storefront_flow, require_test_data)
    data = require_test_data(*expected_amounts.values())
    before_subtotal = cart.summary_amount("Subtotal")
    cart.increase_quantity(data.product_name)
    expect(cart.quantity_input(data.product_name)).to_have_value("2")
    assert cart.summary_amount("Subtotal") > before_subtotal
    for label, data_field in expected_amounts.items():
        assert cart.summary_amount(label) == pytest.approx(
            float(getattr(data, data_field))
        )


@pytest.mark.source_case("TC-CART-009")
def test_last_item_removal_shows_exact_empty_state(
    storefront_flow, require_test_data
) -> None:
    cart, data = prepared_cart(storefront_flow, require_test_data)
    cart.remove_item(data.product_name)
    expect(cart.page.get_by_text("Your Cart is Empty", exact=True)).to_be_visible()
    cart.assert_checkout_disabled()
    expect(
        cart.page.get_by_role("link", name=cart.continue_shopping_label)
        .or_(cart.page.get_by_role("button", name=cart.continue_shopping_label))
        .first
    ).to_be_visible()


@pytest.mark.source_case("TC-CART-010")
def test_unavailable_cart_item_blocks_checkout(
    storefront_cart_page: CartPage, require_test_data
) -> None:
    data = require_test_data("unavailable_cart_path", "product_name")
    storefront_cart_page.open_path(data.unavailable_cart_path)
    storefront_cart_page.assert_out_of_stock(data.product_name)
    storefront_cart_page.assert_checkout_disabled()


@pytest.mark.source_case("TC-CART-011")
def test_valid_cart_can_open_checkout(storefront_flow, require_test_data) -> None:
    cart, _ = prepared_cart(storefront_flow, require_test_data)
    cart.assert_checkout_enabled()
    cart.proceed_to_checkout()
    expect(cart.page).to_have_url(re.compile(re.escape(cart.config.checkout_path)))


@pytest.mark.source_case("TC-CART-012")
@pytest.mark.resilience
def test_inventory_transition_blocks_checkout(
    storefront_flow, require_test_data
) -> None:
    cart, data = prepared_cart(storefront_flow, require_test_data)
    data = require_test_data("inventory_zero_endpoint", "inventory_restore_endpoint")
    response = cart.page.request.post(data.inventory_zero_endpoint)
    assert response.ok, f"Inventory-control endpoint returned HTTP {response.status}"
    try:
        cart.reload()
        cart.assert_out_of_stock(data.product_name)
        cart.assert_checkout_disabled()
    finally:
        restore = cart.page.request.post(data.inventory_restore_endpoint)
        assert restore.ok, f"Inventory restore endpoint returned HTTP {restore.status}"


@pytest.mark.source_case("TC-CART-013")
@pytest.mark.resilience
def test_failed_quantity_update_is_atomic_and_retryable(
    storefront_flow, require_test_data
) -> None:
    cart, data = prepared_cart(storefront_flow, require_test_data)
    initial_quantity = cart.quantity_value(data.product_name)
    initial_subtotal = cart.summary_amount("Subtotal")
    pattern = re.compile(r"/store/carts/.*/line-items/.*")
    cart.page.route(
        pattern,
        lambda route: route.fulfill(
            status=503, json={"message": "Controlled network failure"}
        ),
        times=1,
    )
    cart.increase_quantity(data.product_name)
    expect(
        cart.page.get_by_role("alert")
        .or_(
            cart.page.get_by_text(
                re.compile(r"error|failed|try again|network", re.IGNORECASE)
            )
        )
        .first
    ).to_be_visible()
    expect(cart.quantity_input(data.product_name)).to_have_value(str(initial_quantity))
    assert cart.summary_amount("Subtotal") == initial_subtotal
    cart.increase_quantity(data.product_name)
    expect(cart.quantity_input(data.product_name)).to_have_value(
        str(initial_quantity + 1)
    )


@pytest.mark.source_case("TC-CART-014")
@pytest.mark.resilience
def test_cart_is_restored_after_logout_and_login(
    storefront_flow, require_test_data, app_config
) -> None:
    cart, data = prepared_cart(storefront_flow, require_test_data)
    quantity = cart.quantity_value(data.product_name)
    AccountPage(cart.page, app_config).open()
    AccountPage(cart.page, app_config).logout()
    storefront_flow.login()
    cart.open()
    cart.assert_item_visible(data.product_name)
    expect(cart.quantity_input(data.product_name)).to_have_value(str(quantity))


@pytest.mark.source_case("TC-CART-015")
@pytest.mark.partial
def test_cart_core_behavior_in_configured_browser(
    storefront_flow, require_test_data
) -> None:
    cart, data = prepared_cart(storefront_flow, require_test_data)
    cart.increase_quantity(data.product_name)
    cart.decrease_quantity(data.product_name)
    expect(cart.quantity_input(data.product_name)).to_have_value("1")


@pytest.mark.source_case("TC-CART-016")
@pytest.mark.partial
def test_cart_is_usable_at_named_viewports(storefront_flow, require_test_data) -> None:
    cart, data = prepared_cart(storefront_flow, require_test_data)
    for width, height in ((1440, 900), (768, 1024), (390, 844)):
        cart.page.set_viewport_size({"width": width, "height": height})
        cart.open()
        cart.assert_item_visible(data.product_name)
        assert_no_horizontal_overflow(cart.page)
        expect(cart.quantity_input(data.product_name)).to_be_visible()


@pytest.mark.source_case("TC-CART-017")
@pytest.mark.partial
def test_cart_controls_are_keyboard_operable(
    storefront_flow, require_test_data
) -> None:
    cart, _ = prepared_cart(storefront_flow, require_test_data)
    controls = list(visible_controls(cart.page))
    assert controls, "Expected interactive cart controls"
    for control in controls:
        assert_keyboard_reachable(cart.page, control)
