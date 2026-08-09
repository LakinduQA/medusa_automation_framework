from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from playwright.sync_api import APIResponse

from medusa_automation.api.base_client import BaseApiClient


@dataclass(slots=True)
class CheckoutApiClient(BaseApiClient):
    """Checkout completion and delivery-method helpers."""

    def set_shipping_address(self, cart_id: str, **address: Any) -> APIResponse:
        return self.post(f"/carts/{cart_id}/shipping-address", json=address)

    def list_shipping_options(self, cart_id: str) -> APIResponse:
        return self.get(f"/carts/{cart_id}/shipping-methods")

    def add_shipping_method(self, cart_id: str, *, option_id: str) -> APIResponse:
        return self.post(f"/carts/{cart_id}/shipping-methods", json={"option_id": option_id})

    def complete_cart(self, cart_id: str) -> APIResponse:
        return self.post(f"/carts/{cart_id}/complete")
