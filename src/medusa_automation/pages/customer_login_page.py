from __future__ import annotations

import re

from playwright.sync_api import Locator, expect

from medusa_automation.pages.base_page import BasePage


class CustomerLoginPage(BasePage):
    """Customer-facing authentication surface, kept separate from Medusa Admin."""

    email_label = re.compile(r"email", re.IGNORECASE)
    password_label = re.compile(r"password", re.IGNORECASE)
    submit_label = re.compile(
        r"sign in|log in|login|continue with email", re.IGNORECASE
    )

    @property
    def email(self) -> Locator:
        return (
            self.page.get_by_label(self.email_label)
            .or_(self.page.get_by_placeholder(self.email_label))
            .or_(self.page.locator("input[name='email'], input[type='email']"))
            .first
        )

    @property
    def password(self) -> Locator:
        return (
            self.page.get_by_label(self.password_label)
            .or_(self.page.get_by_placeholder(self.password_label))
            .or_(self.page.locator("input[name='password'], input[type='password']"))
            .first
        )

    @property
    def submit(self) -> Locator:
        return self.page.get_by_role("button", name=self.submit_label).first

    @property
    def visibility_toggle(self) -> Locator:
        return (
            self.page.get_by_role(
                "button",
                name=re.compile(
                    r"show password|hide password|password visibility", re.IGNORECASE
                ),
            )
            .or_(self.page.locator("[data-testid='password-visibility-toggle']"))
            .first
        )

    def open(self) -> None:
        self.open_path(self.config.customer_login_path)

    def login(self, email: str, password: str) -> None:
        self.email.fill(email)
        self.password.fill(password)
        self.submit.click()

    def assert_controls(self) -> None:
        expect(self.email).to_be_visible()
        expect(self.password).to_be_visible()
        expect(self.visibility_toggle).to_be_visible()
        expect(self.submit).to_be_visible()

    def assert_native_validation(
        self, field: Locator, *, kind: str, expected_message: str | None = None
    ) -> None:
        state = field.evaluate(
            """element => ({
                valueMissing: element.validity.valueMissing,
                typeMismatch: element.validity.typeMismatch,
                message: element.validationMessage
            })"""
        )
        assert state[kind], f"Expected native validation {kind}; state was {state}"
        assert state["message"], "Expected the browser to expose a validation message"
        if expected_message:
            assert state["message"] == expected_message, state

    def assert_login_rejected(self, message: str = "Invalid email or password") -> None:
        expect(
            self.page.get_by_role("alert").or_(self.page.get_by_text(message)).first
        ).to_contain_text(message)
        expect(self.page).to_have_url(
            re.compile(re.escape(self.config.customer_login_path))
        )
