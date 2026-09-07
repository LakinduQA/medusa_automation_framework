from __future__ import annotations

import re

from playwright.sync_api import Locator, expect

from medusa_automation.pages.base_page import BasePage


class AccountPage(BasePage):
    @property
    def logout_control(self) -> Locator:
        return (
            self.page.get_by_role(
                "button", name=re.compile(r"log out|logout|sign out", re.IGNORECASE)
            )
            .or_(
                self.page.get_by_role(
                    "link", name=re.compile(r"log out|logout|sign out", re.IGNORECASE)
                )
            )
            .first
        )

    def open(self) -> None:
        self.open_path(self.config.customer_account_path)

    def assert_loaded(self) -> None:
        expect(self.page).to_have_url(
            re.compile(re.escape(self.config.customer_account_path))
        )
        expect(
            self.page.get_by_role(
                "heading", name=re.compile(r"account|profile", re.IGNORECASE)
            )
            .or_(self.logout_control)
            .first
        ).to_be_visible()

    def logout(self) -> None:
        self.logout_control.click()
