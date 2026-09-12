from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from medusa_automation.config import AppConfig
from medusa_automation.pages import (
    AccountPage,
    CartPage,
    CheckoutAddress,
    CheckoutPage,
    CustomerLoginPage,
    ProductPage,
)
from medusa_automation.test_data import StorefrontTestData


class StorefrontFlow:
    """Business-level setup journeys shared by the source-case tests."""

    def __init__(self, page: Page, config: AppConfig, data: StorefrontTestData) -> None:
        self.page = page
        self.config = config
        self.data = data

    def login(self) -> None:
        login = CustomerLoginPage(self.page, self.config)
        login.open()
        login.login(self.data.customer_email, self.data.customer_password)
        AccountPage(self.page, self.config).assert_loaded()

    def open_product(self, handle: str | None = None) -> ProductPage:
        product = ProductPage(self.page, self.config)
        product.open_product(handle or self.data.product_handle)
        product.assert_product_heading()
        return product

    def select_default_variant(self, product: ProductPage) -> None:
        color = product.option(self.data.color_option_name, self.data.primary_color)
        if color.count():
            product.select_option(self.data.color_option_name, self.data.primary_color)
        size = product.option(self.data.size_option_name, self.data.primary_size)
        if size.count():
            product.select_option(self.data.size_option_name, self.data.primary_size)

    def add_default_product(self) -> CartPage:
        product = self.open_product()
        self.select_default_variant(product)
        product.add_to_cart()
        cart = CartPage(self.page, self.config)
        cart.open()
        cart.assert_item_visible(self.data.product_name)
        return cart

    def valid_address(self, **overrides: str) -> CheckoutAddress:
        values = {
            "first_name": self.data.first_name,
            "last_name": self.data.last_name,
            "address_1": self.data.address_1,
            "address_2": self.data.address_2,
            "company": self.data.company,
            "city": self.data.city,
            "postal_code": self.data.postal_code,
            "country_code": self.data.country_code,
            "province": self.data.province,
            "phone": self.data.phone,
        }
        values.update(overrides)
        return CheckoutAddress(**values)

    def start_checkout(self) -> CheckoutPage:
        cart = self.add_default_product()
        cart.proceed_to_checkout()
        checkout = CheckoutPage(self.page, self.config)
        checkout.assert_loaded()
        return checkout

    def complete_shipping(self, checkout: CheckoutPage, **overrides: str) -> None:
        checkout.enter_email(overrides.pop("email", self.data.customer_email))
        checkout.fill_shipping_address(self.valid_address(**overrides))
        checkout.continue_to_shipping()
        checkout.assert_step("Delivery")

    def complete_delivery(
        self, checkout: CheckoutPage, option: str | None = None
    ) -> None:
        checkout.choose_shipping_option(option or self.data.standard_shipping)
        checkout.continue_to_payment()
        checkout.assert_step("Payment")

    def complete_payment(
        self, checkout: CheckoutPage, method: str | None = None
    ) -> None:
        checkout.choose_payment_method(method or self.data.manual_payment)
        checkout.continue_to_review()
        checkout.assert_step("Review")

    def reach_review(self) -> CheckoutPage:
        checkout = self.start_checkout()
        self.complete_shipping(checkout)
        self.complete_delivery(checkout)
        self.complete_payment(checkout)
        return checkout

    def assert_redirected_to_login(self) -> None:
        expect(self.page).to_have_url(
            re.compile(re.escape(self.config.customer_login_path))
        )
