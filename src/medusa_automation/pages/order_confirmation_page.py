from __future__ import annotations

import re

from playwright.sync_api import Locator, expect

from medusa_automation.pages.base_page import BasePage


class OrderConfirmationPage(BasePage):
    @property
    def heading(self) -> Locator:
        return self.page.get_by_role(
            "heading",
            name=re.compile(r"thank you|order confirmed|order complete", re.IGNORECASE),
        ).first

    @property
    def order_number(self) -> Locator:
        return (
            self.page.locator("[data-testid='order-number'], [data-order-number]")
            .or_(
                self.page.get_by_text(re.compile(r"order\s*(number|#)", re.IGNORECASE))
            )
            .first
        )

    def assert_loaded(self) -> None:
        expect(self.heading).to_be_visible()

    def assert_message(self, message: str) -> None:
        expect(self.page.get_by_text(message, exact=True)).to_be_visible()

    def assert_no_edit_controls(self) -> None:
        expect(
            self.page.get_by_role(
                "button",
                name=re.compile(r"edit.*(shipping|delivery|payment)", re.IGNORECASE),
            )
        ).to_have_count(0)

    def assert_no_sensitive_values(self, *values: str) -> None:
        body = self.page.locator("body")
        for value in values:
            if value:
                expect(body).not_to_contain_text(value)
