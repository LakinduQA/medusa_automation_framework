from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from medusa_automation.pages import AccountPage, CheckoutPage, OrderConfirmationPage
from tests.support import (
    assert_keyboard_reachable,
    assert_no_horizontal_overflow,
    case,
    visible_controls,
)

pytestmark = [pytest.mark.e2e]

REQUIRED_CHECKOUT_DATA = (
    "customer_email",
    "customer_password",
    "product_handle",
    "product_name",
    "first_name",
    "last_name",
    "address_1",
    "city",
    "postal_code",
    "country_code",
    "phone",
    "standard_shipping",
    "manual_payment",
)


def prepared_checkout(
    storefront_flow, require_test_data
) -> tuple[CheckoutPage, object]:
    data = require_test_data(*REQUIRED_CHECKOUT_DATA)
    storefront_flow.login()
    return storefront_flow.start_checkout(), data


def fill_valid_shipping(
    checkout: CheckoutPage, storefront_flow, data, **overrides: str
) -> None:
    checkout.enter_email(overrides.pop("email", data.customer_email))
    checkout.fill_shipping_address(storefront_flow.valid_address(**overrides))


def reach_delivery(storefront_flow, require_test_data) -> tuple[CheckoutPage, object]:
    checkout, data = prepared_checkout(storefront_flow, require_test_data)
    fill_valid_shipping(checkout, storefront_flow, data)
    checkout.continue_to_shipping()
    checkout.assert_step("Delivery")
    return checkout, data


def reach_payment(storefront_flow, require_test_data) -> tuple[CheckoutPage, object]:
    checkout, data = reach_delivery(storefront_flow, require_test_data)
    checkout.choose_shipping_option(data.standard_shipping)
    checkout.continue_to_payment()
    checkout.assert_step("Payment")
    return checkout, data


def reach_review(storefront_flow, require_test_data) -> tuple[CheckoutPage, object]:
    checkout, data = reach_payment(storefront_flow, require_test_data)
    checkout.choose_payment_method(data.manual_payment)
    checkout.continue_to_review()
    checkout.assert_step("Review")
    return checkout, data


def place_order(
    storefront_flow, require_test_data
) -> tuple[OrderConfirmationPage, object]:
    checkout, data = reach_review(storefront_flow, require_test_data)
    checkout.place_order()
    confirmation = OrderConfirmationPage(checkout.page, checkout.config)
    confirmation.assert_loaded()
    return confirmation, data


@pytest.mark.source_case("TC-CHK-001")
def test_valid_shipping_address_advances_to_delivery(
    storefront_flow, require_test_data
) -> None:
    checkout, data = prepared_checkout(storefront_flow, require_test_data)
    fill_valid_shipping(checkout, storefront_flow, data)
    checkout.continue_to_shipping()
    checkout.assert_step("Delivery")


@pytest.mark.parametrize(
    ("_case_id", "fields"),
    [
        case(
            "TC-CHK-002",
            "TC-CHK-002",
            (
                "first_name",
                "last_name",
                "address_1",
                "postal_code",
                "city",
                "country_code",
                "email",
                "phone",
            ),
        ),
        case("TC-CHK-008", "TC-CHK-008", ("first_name",)),
    ],
)
def test_missing_mandatory_shipping_data_blocks_delivery(
    _case_id: str,
    fields: tuple[str, ...],
    storefront_flow,
    require_test_data,
) -> None:
    checkout, data = prepared_checkout(storefront_flow, require_test_data)
    fill_valid_shipping(checkout, storefront_flow, data)
    for field_name in fields:
        field = checkout.field(field_name)
        original = field.input_value()
        field.fill("")
        checkout.continue_to_shipping()
        checkout.assert_field_error(field_name)
        field.fill(original)


@pytest.mark.source_case("TC-CHK-003")
def test_optional_shipping_fields_may_be_empty(
    storefront_flow, require_test_data
) -> None:
    checkout, data = prepared_checkout(storefront_flow, require_test_data)
    fill_valid_shipping(checkout, storefront_flow, data, company="", province="")
    checkout.continue_to_shipping()
    checkout.assert_step("Delivery")


@pytest.mark.parametrize(
    ("_case_id", "field_name", "invalid_value"),
    [
        case("TC-CHK-004", "TC-CHK-004", "email", "invalid-email"),
        case("TC-CHK-005", "TC-CHK-005", "phone", "not-a-phone"),
    ],
)
def test_invalid_contact_format_blocks_delivery(
    _case_id: str,
    field_name: str,
    invalid_value: str,
    storefront_flow,
    require_test_data,
) -> None:
    checkout, data = prepared_checkout(storefront_flow, require_test_data)
    overrides = {field_name: invalid_value}
    fill_valid_shipping(checkout, storefront_flow, data, **overrides)
    checkout.continue_to_shipping()
    checkout.assert_field_error(field_name)


@pytest.mark.parametrize(
    ("_case_id", "billing_mode"),
    [
        case("TC-CHK-006", "TC-CHK-006", "same"),
        case("TC-CHK-007", "TC-CHK-007", "separate"),
    ],
)
def test_billing_address_mode_is_saved(
    _case_id: str,
    billing_mode: str,
    storefront_flow,
    require_test_data,
) -> None:
    checkout, data = prepared_checkout(storefront_flow, require_test_data)
    fill_valid_shipping(checkout, storefront_flow, data)
    if billing_mode == "same":
        checkout.use_shipping_as_billing()
        expect(checkout.billing_same_as_shipping).to_be_checked()
    else:
        checkout.use_separate_billing()
        checkout.fill_billing_address(
            storefront_flow.valid_address(
                first_name=data.alternate_first_name,
                address_1=data.alternate_address_1,
            )
        )
        expect(checkout.field("first_name", kind="billing")).to_have_value(
            data.alternate_first_name
        )
    checkout.continue_to_shipping()
    checkout.assert_step("Delivery")


@pytest.mark.source_case("TC-CHK-009")
def test_shipping_information_persists_within_checkout_session(
    storefront_flow, require_test_data
) -> None:
    checkout, data = reach_delivery(storefront_flow, require_test_data)
    checkout.edit_step("shipping")
    expect(checkout.field("first_name")).to_have_value(data.first_name)
    expect(checkout.field("address_1")).to_have_value(data.address_1)


@pytest.mark.source_case("TC-CHK-010")
def test_delivery_methods_show_name_cost_and_optional_estimate(
    storefront_flow, require_test_data
) -> None:
    checkout, data = reach_delivery(storefront_flow, require_test_data)
    option = (
        checkout.page.get_by_label(
            re.compile(re.escape(data.standard_shipping), re.IGNORECASE)
        )
        .or_(
            checkout.page.get_by_text(
                re.compile(re.escape(data.standard_shipping), re.IGNORECASE)
            )
        )
        .first
    )
    expect(option).to_be_visible()
    expect(option.locator("xpath=..")).to_contain_text(re.compile(r"\d"))


@pytest.mark.source_case("TC-CHK-011")
def test_delivery_selection_is_required(storefront_flow, require_test_data) -> None:
    checkout, _ = reach_delivery(storefront_flow, require_test_data)
    if checkout.delivery_continue.is_enabled():
        checkout.delivery_continue.click()
        expect(
            checkout.page.get_by_role("alert")
            .or_(
                checkout.page.get_by_text(
                    re.compile(r"select.*delivery|required", re.IGNORECASE)
                )
            )
            .first
        ).to_be_visible()
    else:
        expect(checkout.delivery_continue).to_be_disabled()


@pytest.mark.source_case("TC-CHK-012")
def test_selected_delivery_method_is_saved_and_opens_payment(
    storefront_flow, require_test_data
) -> None:
    checkout, data = reach_delivery(storefront_flow, require_test_data)
    checkout.choose_shipping_option(data.standard_shipping)
    expect(
        checkout.page.get_by_label(
            re.compile(re.escape(data.standard_shipping), re.IGNORECASE)
        ).first
    ).to_be_checked()
    checkout.continue_to_payment()
    checkout.assert_step("Payment")


@pytest.mark.source_case("TC-CHK-013")
def test_shipping_cost_updates_with_delivery_selection(
    storefront_flow, require_test_data
) -> None:
    checkout, data = reach_delivery(storefront_flow, require_test_data)
    data = require_test_data(
        "express_shipping", "standard_shipping_cost", "express_shipping_cost"
    )
    checkout.choose_shipping_option(data.standard_shipping)
    summary = checkout.page.get_by_text(
        re.compile(r"shipping", re.IGNORECASE)
    ).last.locator("xpath=..")
    expect(summary).to_contain_text(data.standard_shipping_cost)
    checkout.choose_shipping_option(data.express_shipping)
    expect(summary).to_contain_text(data.express_shipping_cost)


@pytest.mark.source_case("TC-CHK-014")
def test_manual_payment_is_available_and_selectable(
    storefront_flow, require_test_data
) -> None:
    checkout, data = reach_payment(storefront_flow, require_test_data)
    method = (
        checkout.page.get_by_label(
            re.compile(re.escape(data.manual_payment), re.IGNORECASE)
        )
        .or_(
            checkout.page.get_by_role(
                "radio", name=re.compile(re.escape(data.manual_payment), re.IGNORECASE)
            )
        )
        .first
    )
    expect(method).to_be_visible()
    method.check()
    expect(method).to_be_checked()


@pytest.mark.source_case("TC-CHK-015")
def test_payment_selection_is_required_before_review(
    storefront_flow, require_test_data
) -> None:
    checkout, _ = reach_payment(storefront_flow, require_test_data)
    if checkout.payment_continue.is_enabled():
        checkout.payment_continue.click()
        expect(
            checkout.page.get_by_role("alert")
            .or_(
                checkout.page.get_by_text(
                    re.compile(r"select.*payment|required", re.IGNORECASE)
                )
            )
            .first
        ).to_be_visible()
    else:
        expect(checkout.payment_continue).to_be_disabled()


@pytest.mark.parametrize(
    ("_case_id", "failure_mode"),
    [
        case("TC-CHK-016", "TC-CHK-016", "server", resilience=True),
        case("TC-CHK-018", "TC-CHK-018", "timedout", resilience=True),
        case("TC-CHK-019", "TC-CHK-019", "internetdisconnected", resilience=True),
    ],
)
def test_payment_disruption_does_not_create_order_and_allows_retry(
    _case_id: str,
    failure_mode: str,
    storefront_flow,
    require_test_data,
) -> None:
    checkout, data = reach_payment(storefront_flow, require_test_data)
    completed_orders: list[str] = []
    checkout.page.on(
        "response",
        lambda response: (
            completed_orders.append(response.url)
            if re.search(r"/store/carts/.*/complete", response.url) and response.ok
            else None
        ),
    )

    def disrupt(route) -> None:
        if failure_mode == "server":
            route.fulfill(status=500, json={"message": "Controlled payment failure"})
        else:
            route.abort(failure_mode)

    checkout.page.route(data.payment_failure_pattern, disrupt, times=1)
    checkout.choose_payment_method(data.manual_payment)
    checkout.continue_to_review()
    expect(
        checkout.page.get_by_role("alert")
        .or_(
            checkout.page.get_by_text(
                re.compile(r"error|failed|timeout|network|try again", re.IGNORECASE)
            )
        )
        .first
    ).to_be_visible()
    expect(
        checkout.page.get_by_role(
            "heading", name=re.compile(r"thank you", re.IGNORECASE)
        )
    ).to_have_count(0)
    assert not completed_orders, (
        "A successful cart completion occurred during payment failure"
    )
    checkout.choose_payment_method(data.manual_payment)
    checkout.continue_to_review()
    checkout.assert_step("Review")


@pytest.mark.source_case("TC-CHK-017")
@pytest.mark.resilience
def test_cancelled_payment_retains_checkout_information(
    storefront_flow, require_test_data
) -> None:
    checkout, data = reach_payment(storefront_flow, require_test_data)
    data = require_test_data("payment_cancel_label")
    checkout.choose_payment_method(data.manual_payment)
    checkout.page.get_by_role(
        "button", name=re.compile(re.escape(data.payment_cancel_label), re.IGNORECASE)
    ).click()
    checkout.assert_step("Payment")
    checkout.edit_step("shipping")
    expect(checkout.field("first_name")).to_have_value(data.first_name)


@pytest.mark.source_case("TC-CHK-020")
def test_review_page_matches_checkout_data(storefront_flow, require_test_data) -> None:
    checkout, data = reach_review(storefront_flow, require_test_data)
    data = require_test_data(
        "expected_checkout_subtotal",
        "expected_checkout_shipping",
        "expected_checkout_tax",
        "expected_checkout_total",
    )
    expected = {
        "Shipping": (data.first_name, data.address_1),
        "Delivery": (data.standard_shipping,),
        "Payment": (data.manual_payment,),
        "Order": (data.product_name,),
    }
    for section, values in expected.items():
        locator = checkout.review_section(section)
        expect(locator).to_be_visible()
        for value in values:
            expect(locator).to_contain_text(value)
    expected_amounts = {
        "Subtotal": data.expected_checkout_subtotal,
        "Shipping": data.expected_checkout_shipping,
        "Tax": data.expected_checkout_tax,
        "Total": data.expected_checkout_total,
    }
    for label, expected_amount in expected_amounts.items():
        row = checkout.page.get_by_text(
            re.compile(rf"^{label}$", re.IGNORECASE)
        ).first.locator("xpath=..")
        expect(row).to_contain_text(expected_amount)


@pytest.mark.source_case("TC-CHK-021")
def test_place_order_is_unavailable_for_incomplete_checkout(
    storefront_flow, require_test_data
) -> None:
    checkout, _ = reach_payment(storefront_flow, require_test_data)
    checkout.assert_place_order_unavailable()


@pytest.mark.parametrize(
    "_case_id",
    [
        case("TC-CHK-022", "TC-CHK-022"),
        case("TC-CHK-025", "TC-CHK-025"),
        case("TC-CHK-026", "TC-CHK-026"),
    ],
)
def test_successful_order_shows_confirmation_and_details(
    _case_id: str, storefront_flow, require_test_data
) -> None:
    confirmation, data = place_order(storefront_flow, require_test_data)
    data = require_test_data(
        "expected_checkout_subtotal",
        "expected_checkout_shipping",
        "expected_checkout_tax",
        "expected_checkout_total",
    )
    confirmation.assert_message(data.confirmation_message)
    expect(confirmation.order_number).to_be_visible()
    body = confirmation.page.locator("body")
    for expected in (
        data.product_name,
        data.first_name,
        data.address_1,
        data.standard_shipping,
        data.manual_payment,
    ):
        expect(body).to_contain_text(expected)
    for expected_amount in (
        data.expected_checkout_subtotal,
        data.expected_checkout_shipping,
        data.expected_checkout_tax,
        data.expected_checkout_total,
    ):
        expect(body).to_contain_text(expected_amount)


@pytest.mark.source_case("TC-CHK-023")
def test_checkout_information_can_be_edited_before_order(
    storefront_flow, require_test_data
) -> None:
    checkout, data = reach_review(storefront_flow, require_test_data)
    checkout.edit_step("shipping")
    checkout.field("first_name").fill(data.alternate_first_name)
    checkout.continue_to_shipping()
    checkout.choose_shipping_option(data.express_shipping)
    checkout.continue_to_payment()
    checkout.choose_payment_method(data.manual_payment)
    checkout.continue_to_review()
    expect(checkout.review_section("Shipping")).to_contain_text(
        data.alternate_first_name
    )
    expect(checkout.review_section("Delivery")).to_contain_text(data.express_shipping)


@pytest.mark.source_case("TC-CHK-024")
def test_submitted_order_cannot_be_edited(storefront_flow, require_test_data) -> None:
    confirmation, _ = place_order(storefront_flow, require_test_data)
    confirmation.assert_no_edit_controls()


@pytest.mark.source_case("TC-CHK-027")
@pytest.mark.resilience
def test_refresh_confirmation_does_not_duplicate_order(
    storefront_flow, require_test_data
) -> None:
    checkout, _ = reach_review(storefront_flow, require_test_data)
    completions: list[str] = []
    checkout.page.on(
        "response",
        lambda response: (
            completions.append(response.url)
            if re.search(r"/store/carts/.*/complete", response.url) and response.ok
            else None
        ),
    )
    checkout.place_order()
    confirmation = OrderConfirmationPage(checkout.page, checkout.config)
    confirmation.assert_loaded()
    order_number = confirmation.order_number.inner_text()
    assert len(completions) == 1, (
        f"Expected one successful completion request: {completions}"
    )
    confirmation.reload()
    confirmation.assert_loaded()
    expect(confirmation.order_number).to_have_text(order_number)
    assert len(completions) == 1, "Refreshing confirmation created another order"


@pytest.mark.source_case("TC-CHK-028")
@pytest.mark.resilience
def test_expired_checkout_session_redirects_to_login(
    storefront_flow, require_test_data
) -> None:
    checkout, data = reach_delivery(storefront_flow, require_test_data)
    data = require_test_data("session_expiry_endpoint")
    response = checkout.page.request.post(data.session_expiry_endpoint)
    assert response.ok, f"Session-expiry endpoint returned HTTP {response.status}"
    checkout.reload()
    storefront_flow.assert_redirected_to_login()


@pytest.mark.source_case("TC-CHK-029")
@pytest.mark.partial
def test_checkout_core_flow_in_configured_browser(
    storefront_flow, require_test_data
) -> None:
    checkout, _ = reach_review(storefront_flow, require_test_data)
    checkout.assert_step("Review")


@pytest.mark.source_case("TC-CHK-030")
@pytest.mark.partial
def test_checkout_is_usable_at_named_viewports(
    storefront_flow, require_test_data
) -> None:
    checkout, _ = prepared_checkout(storefront_flow, require_test_data)
    for width, height in ((1440, 900), (768, 1024), (390, 844)):
        checkout.page.set_viewport_size({"width": width, "height": height})
        checkout.open()
        checkout.assert_loaded()
        assert_no_horizontal_overflow(checkout.page)
        for field in (
            "email",
            "first_name",
            "last_name",
            "address_1",
            "city",
            "postal_code",
        ):
            expect(checkout.field(field)).to_be_visible()


@pytest.mark.source_case("TC-CHK-31")
@pytest.mark.partial
def test_checkout_keyboard_navigation_and_error_feedback(
    storefront_flow, require_test_data
) -> None:
    checkout, _ = prepared_checkout(storefront_flow, require_test_data)
    controls = list(visible_controls(checkout.page))
    assert controls, "Expected interactive checkout controls"
    for control in controls:
        assert_keyboard_reachable(checkout.page, control)
    checkout.continue_to_shipping()
    checkout.assert_field_error("first_name")


@pytest.mark.source_case("TC-CHK-032")
def test_checkout_is_protected_after_logout(
    storefront_flow, require_test_data, app_config
) -> None:
    checkout, _ = prepared_checkout(storefront_flow, require_test_data)
    checkout_url = checkout.page.url
    account = AccountPage(checkout.page, app_config)
    account.open()
    account.logout()
    checkout.page.goto(checkout_url, wait_until="domcontentloaded")
    storefront_flow.assert_redirected_to_login()


@pytest.mark.source_case("TC-CHK-033")
def test_confirmation_does_not_expose_credentials(
    storefront_flow, require_test_data
) -> None:
    confirmation, data = place_order(storefront_flow, require_test_data)
    data = require_test_data("payment_sensitive_sentinel")
    confirmation.assert_no_sensitive_values(
        data.customer_password, data.payment_sensitive_sentinel
    )
    confirmation.page.go_back(wait_until="domcontentloaded")
    confirmation.assert_no_sensitive_values(
        data.customer_password, data.payment_sensitive_sentinel
    )


@pytest.mark.source_case("TC-CHK-034")
def test_shipping_error_is_clear_and_recoverable(
    storefront_flow, require_test_data
) -> None:
    checkout, data = prepared_checkout(storefront_flow, require_test_data)
    fill_valid_shipping(checkout, storefront_flow, data, first_name="")
    checkout.continue_to_shipping()
    checkout.assert_field_error("first_name")
    checkout.field("first_name").fill(data.first_name)
    checkout.continue_to_shipping()
    checkout.assert_step("Delivery")
