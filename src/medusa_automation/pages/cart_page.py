from __future__ import annotations

import re

from playwright.sync_api import Locator, expect

from medusa_automation.pages.base_page import BasePage


class CartPage(BasePage):
    """Storefront cart actions using accessible names and stable item containers."""

    heading_label = re.compile(r"shopping cart|your cart|cart", re.IGNORECASE)
    empty_cart_label = re.compile(r"cart is empty|empty cart|no items", re.IGNORECASE)
    checkout_label = re.compile(r"checkout|proceed to checkout", re.IGNORECASE)
    continue_shopping_label = re.compile(r"continue shopping|back to shop", re.IGNORECASE)
    remove_label = re.compile(r"remove|delete", re.IGNORECASE)
    quantity_label = re.compile(r"quantity", re.IGNORECASE)
    subtotal_label = re.compile(r"subtotal", re.IGNORECASE)

    def open(self) -> None:
        self.open_path(self.config.cart_path)

    def line_item(self, product_name: str) -> Locator:
        item_name = re.compile(re.escape(product_name), re.IGNORECASE)
        return self.page.locator(
            "[data-testid='cart-item'], [data-cart-item], article, li, tr"
        ).filter(has_text=item_name).first

    def quantity_input(self, product_name: str) -> Locator:
        item = self.line_item(product_name)
        return item.get_by_role("spinbutton", name=self.quantity_label).or_(
            item.locator("input[type='number']")
        ).first

    def assert_loaded(self) -> None:
        expect(self.page.get_by_role("heading", name=self.heading_label).first).to_be_visible()

    def assert_empty(self) -> None:
        expect(self.page.get_by_text(self.empty_cart_label).first).to_be_visible()

    def assert_item_visible(self, product_name: str) -> None:
        expect(self.line_item(product_name)).to_be_visible()

    def assert_item_removed(self, product_name: str) -> None:
        expect(self.line_item(product_name)).to_have_count(0)

    def update_quantity(self, product_name: str, quantity: int) -> None:
        if quantity < 1:
            raise ValueError("quantity must be at least 1; use remove_item to delete an item")
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
        self.line_item(product_name).get_by_role("button", name=self.remove_label).click()

    def subtotal(self) -> Locator:
        return self.page.get_by_text(self.subtotal_label).first.locator("xpath=..")

    def proceed_to_checkout(self) -> None:
        self.page.get_by_role("link", name=self.checkout_label).or_(
            self.page.get_by_role("button", name=self.checkout_label)
        ).first.click()

    def continue_shopping(self) -> None:
        self.page.get_by_role("link", name=self.continue_shopping_label).or_(
            self.page.get_by_role("button", name=self.continue_shopping_label)
        ).first.click()
