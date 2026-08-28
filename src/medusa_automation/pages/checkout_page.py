from __future__ import annotations

from dataclasses import dataclass
import re

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

    def open(self) -> None:
        self.open_path(self.config.checkout_path)

    def assert_loaded(self) -> None:
        expect(self.page.get_by_role("heading", name=self.heading_label).first).to_be_visible()

    def enter_email(self, email: str) -> None:
        self.page.get_by_label(self.email_label).first.fill(email)

    def _address_container(self, kind: str) -> Locator:
        label = re.compile(rf"{re.escape(kind)} address", re.IGNORECASE)
        return self.page.get_by_role("group", name=label).or_(
            self.page.locator("fieldset, form, section").filter(has_text=label)
        ).first

    @staticmethod
    def _fill_optional(container: Locator, label: re.Pattern[str], value: str) -> None:
        field = container.get_by_label(label).first
        if value and field.count():
            field.fill(value)

    @staticmethod
    def _set_country(container: Locator, label: re.Pattern[str], country_code: str) -> None:
        field = container.get_by_label(label).first
        tag_name = field.evaluate("element => element.tagName.toLowerCase()")
        if tag_name == "select":
            field.select_option(value=country_code.lower())
        else:
            field.fill(country_code)

    def fill_address(self, kind: str, address: CheckoutAddress) -> None:
        if kind not in {"shipping", "billing"}:
            raise ValueError("kind must be 'shipping' or 'billing'")

        container = self._address_container(kind)
        container.get_by_label(self.first_name_label).first.fill(address.first_name)
        container.get_by_label(self.last_name_label).first.fill(address.last_name)
        container.get_by_label(self.address_1_label).first.fill(address.address_1)
        container.get_by_label(self.city_label).first.fill(address.city)
        container.get_by_label(self.postal_code_label).first.fill(address.postal_code)
        self._set_country(container, self.country_label, address.country_code)
        self._fill_optional(container, self.address_2_label, address.address_2)
        self._fill_optional(container, self.company_label, address.company)
        self._fill_optional(container, self.province_label, address.province)
        self._fill_optional(container, self.phone_label, address.phone)

    def fill_shipping_address(self, address: CheckoutAddress) -> None:
        self.fill_address("shipping", address)

    def fill_billing_address(self, address: CheckoutAddress) -> None:
        self.fill_address("billing", address)

    def use_shipping_as_billing(self) -> None:
        checkbox = self.page.get_by_role(
            "checkbox",
            name=re.compile(r"same as shipping|use shipping.*billing", re.IGNORECASE),
        )
        if not checkbox.is_checked():
            checkbox.check()

    def continue_to_shipping(self) -> None:
        self.page.get_by_role(
            "button",
            name=re.compile(r"continue.*shipping|to shipping|save.*address", re.IGNORECASE),
        ).click()

    def choose_shipping_option(self, option_name: str) -> None:
        option = re.compile(re.escape(option_name), re.IGNORECASE)
        self.page.get_by_role("radio", name=option).or_(
            self.page.get_by_label(option)
        ).first.check()

    def continue_to_payment(self) -> None:
        self.page.get_by_role(
            "button",
            name=re.compile(r"continue.*payment|to payment|save.*shipping", re.IGNORECASE),
        ).click()

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
        confirmation = re.compile(r"order confirmed|thank you|order complete", re.IGNORECASE)
        expect(self.page.get_by_role("heading", name=confirmation).first).to_be_visible()
