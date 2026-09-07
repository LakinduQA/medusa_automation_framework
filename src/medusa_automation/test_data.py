from __future__ import annotations

import os
from dataclasses import dataclass, fields


def _value(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


@dataclass(frozen=True, slots=True)
class StorefrontTestData:
    """Environment-backed, non-secret test-data contract for storefront E2E tests."""

    customer_email: str = ""
    customer_password: str = ""
    product_handle: str = ""
    product_name: str = ""
    related_product_name: str = ""
    no_related_product_handle: str = ""
    out_of_stock_product_handle: str = ""
    limited_stock_product_handle: str = ""
    limited_stock_product_name: str = ""
    unavailable_combination_product_handle: str = ""
    unavailable_cart_path: str = ""
    inventory_zero_endpoint: str = ""
    session_expiry_endpoint: str = ""
    payment_failure_pattern: str = "**/store/payment-collections/**"
    payment_cancel_label: str = ""
    payment_sensitive_sentinel: str = ""
    color_option_name: str = "Color"
    primary_color: str = "Black"
    secondary_color: str = "White"
    size_option_name: str = "Size"
    primary_size: str = "M"
    secondary_size: str = "L"
    filter_name: str = "Size"
    filter_value: str = "L"
    filter_expected_product_names: str = ""
    latest_product_name: str = ""
    standard_shipping: str = "Standard Shipping"
    express_shipping: str = "Express Shipping"
    manual_payment: str = "Manual Payment"
    confirmation_message: str = "Thank you! Your order was placed successfully."
    required_field_message: str = "Please fill out this field."
    expected_subtotal_qty_2: str = ""
    expected_shipping_qty_2: str = ""
    expected_tax_qty_2: str = ""
    expected_total_qty_2: str = ""
    standard_shipping_cost: str = ""
    express_shipping_cost: str = ""
    expected_checkout_subtotal: str = ""
    expected_checkout_shipping: str = ""
    expected_checkout_tax: str = ""
    expected_checkout_total: str = ""
    first_name: str = "Playwright"
    last_name: str = "Customer"
    address_1: str = "1 Test Street"
    address_2: str = ""
    company: str = ""
    city: str = "Colombo"
    postal_code: str = "00100"
    country_code: str = "lk"
    province: str = ""
    phone: str = "+94770000000"
    alternate_first_name: str = "Updated"
    alternate_address_1: str = "2 Test Street"
    inventory_limit: str = "5"
    inventory_restore_endpoint: str = ""

    @classmethod
    def from_env(cls) -> StorefrontTestData:
        defaults = cls()
        values = {
            field.name: _value(
                f"TEST_{field.name.upper()}", getattr(defaults, field.name)
            )
            for field in fields(cls)
        }
        return cls(**values)

    def missing(self, *names: str) -> list[str]:
        unknown = [name for name in names if not hasattr(self, name)]
        if unknown:
            raise ValueError(
                f"Unknown storefront test-data fields: {', '.join(unknown)}"
            )
        return [name for name in names if not str(getattr(self, name)).strip()]
