from __future__ import annotations

import re
from dataclasses import dataclass

from playwright.sync_api import Locator, expect

from medusa_automation.pages.base_page import BasePage


@dataclass(frozen=True, slots=True)
class CheckoutAddress:
    first_name: str
    last_name: str
    address_1: str
    city: str
    postal_code: str
    country_code: str
    address_2: str = ""
    company: str = ""
    province: str = ""
    phone: str = ""


class CheckoutPage(BasePage):
    """Storefront checkout actions for contact, delivery, and payment steps."""

    heading_label = re.compile(r"checkout", re.IGNORECASE)
    email_label = re.compile(r"email", re.IGNORECASE)
    first_name_label = re.compile(r"first name", re.IGNORECASE)
    last_name_label = re.compile(r"last name", re.IGNORECASE)
    address_1_label = re.compile(r"address( line)? 1|street address", re.IGNORECASE)
    address_2_label = re.compile(r"address( line)? 2|apartment|suite", re.IGNORECASE)
    company_label = re.compile(r"company", re.IGNORECASE)
    city_label = re.compile(r"city", re.IGNORECASE)
    postal_code_label = re.compile(r"postal|zip", re.IGNORECASE)
    country_label = re.compile(r"country", re.IGNORECASE)
    province_label = re.compile(r"province|state|region", re.IGNORECASE)
    phone_label = re.compile(r"phone", re.IGNORECASE)
    place_order_label = re.compile(r"place order|complete order|pay now", re.IGNORECASE)

    @property
    def billing_same_as_shipping(self) -> Locator:
        return self.page.get_by_role(
            "checkbox",
            name=re.compile(r"same as shipping|use shipping.*billing", re.IGNORECASE),
        ).first

    @property
    def delivery_continue(self) -> Locator:
        return self.page.get_by_role(
            "button",
            name=re.compile(
                r"continue.*payment|to payment|save.*shipping", re.IGNORECASE
            ),
        ).first

    @property
    def payment_continue(self) -> Locator:
        return self.page.get_by_role(
            "button",
            name=re.compile(r"continue.*review|to review|review order", re.IGNORECASE),
        ).first

    def open(self) -> None:
        self.open_path(self.config.checkout_path)

    def assert_loaded(self) -> None:
        expect(
            self.page.get_by_role("heading", name=self.heading_label).first
        ).to_be_visible()

    def enter_email(self, email: str) -> None:
        self.field("email").fill(email)

    def field(self, name: str, *, kind: str = "shipping") -> Locator:
        labels = {
            "email": self.email_label,
            "first_name": self.first_name_label,
            "last_name": self.last_name_label,
            "address_1": self.address_1_label,
            "address_2": self.address_2_label,
            "company": self.company_label,
            "city": self.city_label,
            "postal_code": self.postal_code_label,
            "country_code": self.country_label,
            "province": self.province_label,
            "phone": self.phone_label,
        }
        try:
            label = labels[name]
        except KeyError as exc:
            raise ValueError(f"Unknown checkout field: {name}") from exc
        if name == "email":
            return (
                self.page.get_by_label(label)
                .or_(self.page.get_by_placeholder(label))
                .or_(self.page.locator("input[name='email'], input[type='email']"))
                .first
            )
        container = self._address_container(kind)
        return (
            container.get_by_label(label)
            .or_(container.get_by_placeholder(label))
            .or_(container.locator(f"[name='{name}']"))
            .first
        )

    def _address_container(self, kind: str) -> Locator:
        label = re.compile(rf"{re.escape(kind)} address", re.IGNORECASE)
        candidate = (
            self.page.get_by_role("group", name=label)
            .or_(self.page.locator("fieldset, form, section").filter(has_text=label))
            .first
        )
        return candidate if candidate.count() else self.page.locator("main, body").first

    def fill_address(self, kind: str, address: CheckoutAddress) -> None:
        if kind not in {"shipping", "billing"}:
            raise ValueError("kind must be 'shipping' or 'billing'")

        self.field("first_name", kind=kind).fill(address.first_name)
        self.field("last_name", kind=kind).fill(address.last_name)
        self.field("address_1", kind=kind).fill(address.address_1)
        self.field("city", kind=kind).fill(address.city)
        self.field("postal_code", kind=kind).fill(address.postal_code)
        country = self.field("country_code", kind=kind)
        tag_name = country.evaluate("element => element.tagName.toLowerCase()")
        if tag_name == "select":
            country.select_option(value=address.country_code.lower())
        else:
            country.fill(address.country_code)
        optional_values = {
            "address_2": address.address_2,
            "company": address.company,
            "province": address.province,
            "phone": address.phone,
        }
        for field_name, value in optional_values.items():
            field = self.field(field_name, kind=kind)
            if value and field.count():
                field.fill(value)

    def fill_shipping_address(self, address: CheckoutAddress) -> None:
        self.fill_address("shipping", address)

    def fill_billing_address(self, address: CheckoutAddress) -> None:
        self.fill_address("billing", address)

    def use_shipping_as_billing(self) -> None:
        checkbox = self.billing_same_as_shipping
        if not checkbox.is_checked():
            checkbox.check()

    def use_separate_billing(self) -> None:
        checkbox = self.billing_same_as_shipping
        if checkbox.is_checked():
            checkbox.uncheck()

    def continue_to_shipping(self) -> None:
        self.page.get_by_role(
            "button",
            name=re.compile(
                r"continue.*shipping|to shipping|save.*address", re.IGNORECASE
            ),
        ).click()

    def assert_step(self, name: str) -> None:
        expect(
            self.page.get_by_role(
                "heading", name=re.compile(re.escape(name), re.IGNORECASE)
            )
            .or_(
                self.page.get_by_text(
                    re.compile(rf"^{re.escape(name)}$", re.IGNORECASE)
                )
            )
            .first
        ).to_be_visible()

    def assert_field_error(self, field_name: str, *, kind: str = "shipping") -> None:
        field = self.field(field_name, kind=kind)
        invalid = field.get_attribute("aria-invalid") == "true" or field.evaluate(
            "element => !element.validity.valid"
        )
        assert invalid, f"Expected {kind} field {field_name!r} to be invalid"
        described_by = field.get_attribute("aria-describedby")
        if described_by:
            expect(self.page.locator(f"#{described_by}")).to_be_visible()
        else:
            expect(
                self.page.get_by_role("alert")
                .or_(
                    self.page.get_by_text(
                        re.compile(r"required|invalid|enter", re.IGNORECASE)
                    )
                )
                .first
            ).to_be_visible()

    def shipping_options(self) -> Locator:
        return self.page.get_by_role(
            "radio", name=re.compile(r"shipping|delivery", re.IGNORECASE)
        ).or_(self.page.locator("[data-testid='shipping-option'] input[type='radio']"))

    def payment_options(self) -> Locator:
        return self.page.get_by_role(
            "radio", name=re.compile(r"payment", re.IGNORECASE)
        ).or_(self.page.locator("[data-testid='payment-option'] input[type='radio']"))

    def continue_to_review(self) -> None:
        self.payment_continue.click()

    def edit_step(self, name: str) -> None:
        self.page.get_by_role(
            "button", name=re.compile(rf"edit.*{re.escape(name)}", re.IGNORECASE)
        ).or_(
            self.page.get_by_role(
                "link", name=re.compile(rf"edit.*{re.escape(name)}", re.IGNORECASE)
            )
        ).first.click()

    def review_section(self, name: str) -> Locator:
        return (
            self.page.locator("section, [data-testid*='review']")
            .filter(has_text=re.compile(re.escape(name), re.IGNORECASE))
            .first
        )

    def summary_amount(self, label: str) -> float:
        row = self.page.get_by_text(
            re.compile(rf"^{re.escape(label)}$", re.IGNORECASE)
        ).first.locator("xpath=..")
        normalized = re.sub(r"[^0-9,.-]", "", row.inner_text()).replace(",", "")
        if not normalized:
            raise AssertionError(f"Could not parse {label!r} from checkout summary")
        return float(normalized)

    def assert_place_order_unavailable(self) -> None:
        button = self.page.get_by_role("button", name=self.place_order_label).first
        if button.count():
            expect(button).to_be_disabled()
        else:
            expect(button).to_have_count(0)

    def choose_shipping_option(self, option_name: str) -> None:
        option = re.compile(re.escape(option_name), re.IGNORECASE)
        self.page.get_by_role("radio", name=option).or_(
            self.page.get_by_label(option)
        ).first.check()

    def continue_to_payment(self) -> None:
        self.delivery_continue.click()

    def choose_payment_method(self, method_name: str) -> None:
        method = re.compile(re.escape(method_name), re.IGNORECASE)
        self.page.get_by_role("radio", name=method).or_(
            self.page.get_by_label(method)
        ).first.check()

    def place_order(self) -> None:
        self.page.get_by_role("button", name=self.place_order_label).click()

    def assert_error(self, message: str | None = None) -> None:
        error = self.page.get_by_role("alert").first
        expect(error).to_be_visible()
        if message:
            expect(error).to_contain_text(message)

    def assert_order_confirmation(self) -> None:
        confirmation = re.compile(
            r"order confirmed|thank you|order complete", re.IGNORECASE
        )
        expect(
            self.page.get_by_role("heading", name=confirmation).first
        ).to_be_visible()
