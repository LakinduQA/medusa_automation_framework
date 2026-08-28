from __future__ import annotations

import re

from playwright.sync_api import expect

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

    def click_product_by_name(self, name: str) -> None:
        self.page.get_by_role("link", name=re.compile(re.escape(name), re.IGNORECASE)).click()

    def assert_product_heading(self, name: str | None = None) -> None:
        heading = self.page.get_by_role("heading", level=1)
        expect(heading).to_be_visible()
        if name:
            expect(heading).to_contain_text(name)

    def assert_product_page_loaded(self) -> None:
        expect(self.page.get_by_text(self.product_name)).to_be_visible()

    def add_to_cart(self) -> None:
        self.page.get_by_role("button", name=self.add_to_cart_label).click()
