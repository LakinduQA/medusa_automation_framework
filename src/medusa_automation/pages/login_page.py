from __future__ import annotations

import re

from playwright.sync_api import expect

from medusa_automation.pages.base_page import BasePage


class LoginPage(BasePage):
    """Login page object with resilient semantic locators."""

    email_label = re.compile(r"email", re.IGNORECASE)
    password_label = re.compile(r"password", re.IGNORECASE)
    submit_label = re.compile(r"sign in|log in|login", re.IGNORECASE)

    def open(self) -> None:
        self.open_admin_path(self.config.login_path)

    def login(self, email: str, password: str) -> None:
        self.page.get_by_label(self.email_label).fill(email)
        self.page.get_by_label(self.password_label).fill(password)
        self.page.get_by_role("button", name=self.submit_label).click()

    def assert_on_login_page(self) -> None:
        expect(self.page.get_by_label(self.email_label)).to_be_visible()
        expect(self.page.get_by_label(self.password_label)).to_be_visible()

    def assert_error_visible(self, message: str | None = None) -> None:
        error_locator = self.page.get_by_role("alert")
        expect(error_locator).to_be_visible()
        if message:
            expect(error_locator).to_contain_text(message)
