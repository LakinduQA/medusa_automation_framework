from __future__ import annotations

import re

from playwright.sync_api import Locator, expect

from medusa_automation.pages.base_page import BasePage


class CartPage(BasePage):
    """Storefront cart actions using accessible names and stable item containers."""

    heading_label = re.compile(r"shopping cart|your cart|cart", re.IGNORECASE)
    empty_cart_label = re.compile(r"cart is empty|empty cart|no items", re.IGNORECASE)
    checkout_label = re.compile(r"checkout|proceed to checkout", re.IGNORECASE)
    continue_shopping_label = re.compile(
        r"continue shopping|back to shop", re.IGNORECASE
    )
    remove_label = re.compile(r"remove|delete", re.IGNORECASE)
    quantity_label = re.compile(r"quantity", re.IGNORECASE)
    subtotal_label = re.compile(r"subtotal", re.IGNORECASE)

    @staticmethod
    def parse_amount(text: str) -> float:
        normalized = re.sub(r"[^0-9,.-]", "", text).replace(",", "")
        if not normalized:
            raise AssertionError(f"Could not parse a monetary amount from {text!r}")
        return float(normalized)

    def open(self) -> None:
        self.open_path(self.config.cart_path)

    def line_item(self, product_name: str) -> Locator:
        item_name = re.compile(re.escape(product_name), re.IGNORECASE)
        return (
            self.page.locator(
                "[data-testid='cart-item'], [data-cart-item], article, li, tr"
            )
            .filter(has_text=item_name)
            .first
        )

    def quantity_input(self, product_name: str) -> Locator:
        item = self.line_item(product_name)
        return (
            item.get_by_role("spinbutton", name=self.quantity_label)
            .or_(item.locator("input[type='number']"))
            .first
        )

    def assert_loaded(self) -> None:
        expect(
            self.page.get_by_role("heading", name=self.heading_label).first
        ).to_be_visible()

    def assert_empty(self) -> None:
        expect(self.page.get_by_text(self.empty_cart_label).first).to_be_visible()

    def assert_item_visible(self, product_name: str) -> None:
        expect(self.line_item(product_name)).to_be_visible()

    def assert_item_removed(self, product_name: str) -> None:
        expect(self.line_item(product_name)).to_have_count(0)

    def update_quantity(self, product_name: str, quantity: int) -> None:
        if quantity < 1:
            raise ValueError(
                "quantity must be at least 1; use remove_item to delete an item"
            )
        quantity_input = self.quantity_input(product_name)
        quantity_input.fill(str(quantity))
        quantity_input.press("Enter")

    def increase_quantity(self, product_name: str) -> None:
        item = self.line_item(product_name)
        item.get_by_role(
            "button",
            name=re.compile(r"increase|increment|add one", re.IGNORECASE),
        ).click()

    def decrease_quantity(self, product_name: str) -> None:
        item = self.line_item(product_name)
        item.get_by_role(
            "button",
            name=re.compile(r"decrease|decrement|remove one", re.IGNORECASE),
        ).click()

    def remove_item(self, product_name: str) -> None:
        self.line_item(product_name).get_by_role(
            "button", name=self.remove_label
        ).click()

    def subtotal(self) -> Locator:
        return self.page.get_by_text(self.subtotal_label).first.locator("xpath=..")

    def summary_row(self, label: str) -> Locator:
        return self.page.get_by_text(
            re.compile(rf"^{re.escape(label)}$", re.IGNORECASE)
        ).first.locator("xpath=..")

    def summary_amount(self, label: str) -> float:
        return self.parse_amount(self.summary_row(label).inner_text())

    def quantity_value(self, product_name: str) -> int:
        return int(self.quantity_input(product_name).input_value())

    def assert_item_details(self, product_name: str, *expected_details: str) -> None:
        item = self.line_item(product_name)
        expect(item).to_be_visible()
        for detail in expected_details:
            expect(item).to_contain_text(detail)
        expect(item).to_contain_text(re.compile(r"\d"))

    def assert_out_of_stock(self, product_name: str) -> None:
        expect(self.line_item(product_name)).to_contain_text(
            re.compile(r"out of stock|unavailable", re.IGNORECASE)
        )

    def checkout_control(self) -> Locator:
        return (
            self.page.get_by_role("link", name=self.checkout_label)
            .or_(self.page.get_by_role("button", name=self.checkout_label))
            .first
        )

    def assert_checkout_enabled(self) -> None:
        expect(self.checkout_control()).to_be_enabled()

    def assert_checkout_disabled(self) -> None:
        control = self.checkout_control()
        disabled = (
            control.get_attribute("aria-disabled") == "true" or not control.is_enabled()
        )
        assert disabled, "Expected Checkout to be unavailable"

    def proceed_to_checkout(self) -> None:
        self.page.get_by_role("link", name=self.checkout_label).or_(
            self.page.get_by_role("button", name=self.checkout_label)
        ).first.click()

    def continue_shopping(self) -> None:
        self.page.get_by_role("link", name=self.continue_shopping_label).or_(
            self.page.get_by_role("button", name=self.continue_shopping_label)
        ).first.click()
