from __future__ import annotations

import re
from uuid import uuid4

import pytest
from playwright.sync_api import Page, expect

from medusa_automation.config import AppConfig
from medusa_automation.pages import AccountPage, CustomerLoginPage
from tests.support import assert_keyboard_reachable, assert_no_horizontal_overflow, case

pytestmark = [pytest.mark.e2e]


@pytest.mark.source_case("TC-LGN-001")
def test_login_displays_required_controls(
    customer_login_page: CustomerLoginPage,
) -> None:
    customer_login_page.open()
    customer_login_page.assert_controls()


@pytest.mark.parametrize(
    "_case_id",
    [
        case("TC-LGN-002", "TC-LGN-002"),
        case("TC-LGN-011", "TC-LGN-011"),
    ],
)
def test_valid_customer_login_creates_session_and_redirects(
    _case_id: str,
    customer_login_page: CustomerLoginPage,
    account_page: AccountPage,
    require_test_data,
) -> None:
    data = require_test_data("customer_email", "customer_password")
    customer_login_page.open()
    customer_login_page.login(data.customer_email, data.customer_password)
    account_page.assert_loaded()


@pytest.mark.source_case("TC-LGN-003")
def test_password_is_masked_by_default(customer_login_page: CustomerLoginPage) -> None:
    customer_login_page.open()
    customer_login_page.password.fill("not-a-secret-fixture-value")
    expect(customer_login_page.password).to_have_attribute("type", "password")


@pytest.mark.source_case("TC-LGN-004")
def test_password_visibility_toggle_preserves_value(
    customer_login_page: CustomerLoginPage,
) -> None:
    value = "not-a-secret-fixture-value"
    customer_login_page.open()
    customer_login_page.password.fill(value)
    customer_login_page.visibility_toggle.click()
    expect(customer_login_page.password).to_have_attribute("type", "text")
    expect(customer_login_page.password).to_have_value(value)
    customer_login_page.visibility_toggle.click()
    expect(customer_login_page.password).to_have_attribute("type", "password")
    expect(customer_login_page.password).to_have_value(value)


@pytest.mark.parametrize(
    ("_case_id", "missing_field"),
    [
        case("TC-LGN-005", "TC-LGN-005", "email"),
        case("TC-LGN-006", "TC-LGN-006", "password"),
    ],
)
def test_required_login_fields_use_browser_validation(
    _case_id: str,
    missing_field: str,
    customer_login_page: CustomerLoginPage,
    require_test_data,
) -> None:
    data = require_test_data("customer_email", "customer_password")
    customer_login_page.open()
    if missing_field != "email":
        customer_login_page.email.fill(data.customer_email)
    if missing_field != "password":
        customer_login_page.password.fill(data.customer_password)
    customer_login_page.submit.click()
    field = (
        customer_login_page.email
        if missing_field == "email"
        else customer_login_page.password
    )
    customer_login_page.assert_native_validation(
        field,
        kind="valueMissing",
        expected_message=data.required_field_message,
    )


@pytest.mark.source_case("TC-LGN-007")
def test_invalid_email_format_is_rejected(
    customer_login_page: CustomerLoginPage, require_test_data
) -> None:
    data = require_test_data("customer_password")
    customer_login_page.open()
    customer_login_page.email.fill("invalid-email")
    customer_login_page.password.fill(data.customer_password)
    customer_login_page.submit.click()
    customer_login_page.assert_native_validation(
        customer_login_page.email, kind="typeMismatch"
    )


@pytest.mark.source_case("TC-LGN-008")
def test_email_outer_whitespace_is_ignored(
    customer_login_page: CustomerLoginPage,
    account_page: AccountPage,
    require_test_data,
) -> None:
    data = require_test_data("customer_email", "customer_password")
    customer_login_page.open()
    customer_login_page.login(f"  {data.customer_email}  ", data.customer_password)
    account_page.assert_loaded()


@pytest.mark.parametrize(
    ("_case_id", "credential_defect"),
    [
        case("TC-LGN-009", "TC-LGN-009", "password"),
        case("TC-LGN-010", "TC-LGN-010", "email"),
    ],
)
def test_invalid_credentials_are_rejected_generically(
    _case_id: str,
    credential_defect: str,
    customer_login_page: CustomerLoginPage,
    require_test_data,
) -> None:
    data = require_test_data("customer_email", "customer_password")
    email = data.customer_email
    password = data.customer_password
    if credential_defect == "email":
        email = f"unregistered-{uuid4().hex}@example.invalid"
    else:
        password = f"wrong-{uuid4().hex}"
    customer_login_page.open()
    customer_login_page.login(email, password)
    customer_login_page.assert_login_rejected()


@pytest.mark.source_case("TC-LGN-012")
def test_logout_terminates_customer_session(
    authenticated_customer_page: Page, app_config: AppConfig
) -> None:
    account = AccountPage(authenticated_customer_page, app_config)
    account.logout()
    account.open()
    expect(authenticated_customer_page).to_have_url(
        re.compile(re.escape(app_config.customer_login_path))
    )


@pytest.mark.source_case("TC-LGN-013")
@pytest.mark.resilience
def test_protected_page_is_inaccessible_after_session_invalidation(
    authenticated_customer_page: Page, app_config: AppConfig, require_test_data
) -> None:
    data = require_test_data("session_expiry_endpoint")
    response = authenticated_customer_page.request.post(data.session_expiry_endpoint)
    assert response.ok, f"Session-expiry endpoint returned HTTP {response.status}"
    AccountPage(authenticated_customer_page, app_config).open()
    expect(authenticated_customer_page).to_have_url(
        re.compile(re.escape(app_config.customer_login_path))
    )


@pytest.mark.source_case("TC-LGN-014")
@pytest.mark.resilience
def test_rapid_submits_create_one_login_request(
    customer_login_page: CustomerLoginPage,
    account_page: AccountPage,
    require_test_data,
) -> None:
    data = require_test_data("customer_email", "customer_password")
    requests: list[str] = []
    customer_login_page.page.on(
        "request",
        lambda request: (
            requests.append(request.url)
            if re.search(r"/auth/.*/emailpass", request.url)
            else None
        ),
    )
    customer_login_page.open()
    customer_login_page.email.fill(data.customer_email)
    customer_login_page.password.fill(data.customer_password)
    customer_login_page.submit.evaluate(
        "button => { button.click(); button.click(); button.click(); }"
    )
    account_page.assert_loaded()
    assert len(requests) == 1, f"Expected one login request, observed {requests}"


@pytest.mark.source_case("TC-LGN-015")
@pytest.mark.partial
def test_login_keyboard_controls_and_error_association(
    customer_login_page: CustomerLoginPage,
) -> None:
    customer_login_page.open()
    for control in (
        customer_login_page.email,
        customer_login_page.password,
        customer_login_page.visibility_toggle,
        customer_login_page.submit,
    ):
        assert_keyboard_reachable(customer_login_page.page, control)
    customer_login_page.password.fill("valid-shape-password")
    customer_login_page.submit.press("Enter")
    customer_login_page.assert_native_validation(
        customer_login_page.email, kind="valueMissing"
    )


@pytest.mark.source_case("TC-LGN-016")
@pytest.mark.partial
def test_login_core_flow_in_configured_browser(
    customer_login_page: CustomerLoginPage,
    account_page: AccountPage,
    require_test_data,
) -> None:
    data = require_test_data("customer_email", "customer_password")
    customer_login_page.open()
    customer_login_page.assert_controls()
    customer_login_page.login(data.customer_email, data.customer_password)
    account_page.assert_loaded()


@pytest.mark.source_case("TC-LGN-017")
@pytest.mark.partial
def test_login_is_usable_at_named_viewports(
    customer_login_page: CustomerLoginPage,
    require_test_data,
) -> None:
    data = require_test_data("customer_email", "customer_password")
    for width, height in ((1440, 900), (768, 1024), (390, 844)):
        customer_login_page.page.set_viewport_size({"width": width, "height": height})
        customer_login_page.open()
        customer_login_page.assert_controls()
        assert_no_horizontal_overflow(customer_login_page.page)
    customer_login_page.login(data.customer_email, data.customer_password)
    AccountPage(customer_login_page.page, customer_login_page.config).assert_loaded()
