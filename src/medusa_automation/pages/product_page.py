from __future__ import annotations

import re

from playwright.sync_api import Locator, expect

from medusa_automation.pages.base_page import BasePage


class ProductPage(BasePage):
    """Reusable product page object for storefront and admin flows."""

    product_name = re.compile(r"product", re.IGNORECASE)
    add_to_cart_label = re.compile(r"add to cart", re.IGNORECASE)
    save_label = re.compile(r"save|publish", re.IGNORECASE)

    def open_catalog(self) -> None:
        self.open_admin_path(self.config.products_path)

    def open_product(self, handle: str) -> None:
        self.page.goto(self.config.product_url(handle), wait_until="domcontentloaded")

    @property
    def add_to_cart_button(self) -> Locator:
        return self.page.get_by_role("button", name=self.add_to_cart_label).first

    @property
    def quantity_input(self) -> Locator:
        return (
            self.page.get_by_role(
                "spinbutton", name=re.compile(r"quantity", re.IGNORECASE)
            )
            .or_(self.page.locator("input[name='quantity'], input[type='number']"))
            .first
        )

    def option(self, option_name: str, value: str) -> Locator:
        option_pattern = re.compile(re.escape(option_name), re.IGNORECASE)
        value_pattern = re.compile(re.escape(value), re.IGNORECASE)
        group = (
            self.page.get_by_role("group", name=option_pattern)
            .or_(
                self.page.locator("fieldset, section, [data-product-option]").filter(
                    has_text=option_pattern
                )
            )
            .first
        )
        return (
            group.get_by_role("radio", name=value_pattern)
            .or_(group.get_by_role("button", name=value_pattern))
            .or_(group.get_by_label(value_pattern))
            .first
        )

    def select_option(self, option_name: str, value: str) -> None:
        control = self.option(option_name, value)
        if (
            control.get_attribute("role") == "radio"
            or control.get_attribute("type") == "radio"
        ):
            control.check()
        else:
            control.click()
        selected = control.evaluate(
            """element => ({
                checked: Boolean(element.checked),
                ariaChecked: element.getAttribute('aria-checked'),
                ariaPressed: element.getAttribute('aria-pressed'),
                state: element.getAttribute('data-state'),
                selected: element.getAttribute('data-selected')
            })"""
        )
        assert any(
            re.search(r"true|checked|on|selected|active", str(value), re.IGNORECASE)
            for value in selected.values()
        ), f"Option {option_name}={value} was not exposed as selected: {selected}"

    def assert_required_details(self) -> None:
        expect(self.page.get_by_role("heading", level=1)).to_be_visible()
        expect(self.page.locator("main img").first).to_be_visible()
        expect(
            self.page.locator(
                "[data-testid='product-description'], [data-product-description], main p"
            ).first
        ).not_to_be_empty()
        expect(
            self.page.locator(
                "[data-testid='product-price'], [data-product-price], [class*='price']"
            ).first
        ).to_contain_text(re.compile(r"\d"))

    def set_quantity(self, quantity: int) -> None:
        self.quantity_input.fill(str(quantity))

    def cart_count(self) -> Locator:
        return self.page.locator(
            "[data-testid='cart-count'], [data-cart-count], a[href*='/cart'] [class*='count']"
        ).first

    def related_products(self) -> Locator:
        heading = self.page.get_by_role(
            "heading", name=re.compile(r"related products", re.IGNORECASE)
        ).first
        return heading.locator(
            "xpath=following::*[self::section or self::div][1]"
        ).locator(
            "[data-testid='product-card'], [data-product-card], article:has(a[href*='/products/'])"
        )

    def click_product_by_name(self, name: str) -> None:
        self.page.get_by_role(
            "link", name=re.compile(re.escape(name), re.IGNORECASE)
        ).click()

    def assert_product_heading(self, name: str | None = None) -> None:
        heading = self.page.get_by_role("heading", level=1)
        expect(heading).to_be_visible()
        if name:
            expect(heading).to_contain_text(name)

    def assert_product_page_loaded(self) -> None:
        expect(self.page.get_by_text(self.product_name)).to_be_visible()

    def add_to_cart(self) -> None:
        self.add_to_cart_button.click()

    def assert_add_to_cart_unavailable(self, message: str | None = None) -> None:
        button = self.add_to_cart_button
        if button.is_visible():
            expect(button).to_be_disabled()
        if message:
            expect(
                self.page.get_by_text(
                    re.compile(re.escape(message), re.IGNORECASE)
                ).first
            ).to_be_visible()
