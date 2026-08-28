from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from playwright.sync_api import APIResponse

from medusa_automation.api.base_client import BaseApiClient


@dataclass(slots=True)
class CheckoutApiClient(BaseApiClient):
    """Medusa v2 checkout, delivery, and payment helpers."""

    def set_email(self, cart_id: str, email: str) -> APIResponse:
        return self.post(f"/carts/{cart_id}", json={"email": email})

    def set_shipping_address(self, cart_id: str, **address: Any) -> APIResponse:
        return self.post(f"/carts/{cart_id}", json={"shipping_address": address})

    def set_billing_address(self, cart_id: str, **address: Any) -> APIResponse:
        return self.post(f"/carts/{cart_id}", json={"billing_address": address})

    def set_addresses(
        self,
        cart_id: str,
        *,
        shipping_address: dict[str, Any],
        billing_address: dict[str, Any] | None = None,
    ) -> APIResponse:
        payload: dict[str, Any] = {"shipping_address": shipping_address}
        if billing_address is not None:
            payload["billing_address"] = billing_address
        return self.post(f"/carts/{cart_id}", json=payload)

    def list_shipping_options(self, cart_id: str) -> APIResponse:
        return self.get("/shipping-options", params={"cart_id": cart_id})

    def add_shipping_method(
        self,
        cart_id: str,
        *,
        option_id: str,
        data: dict[str, Any] | None = None,
    ) -> APIResponse:
        payload: dict[str, Any] = {"option_id": option_id}
        if data is not None:
            payload["data"] = data
        return self.post(f"/carts/{cart_id}/shipping-methods", json=payload)

    def list_payment_providers(self, region_id: str) -> APIResponse:
        return self.get("/payment-providers", params={"region_id": region_id})

    def create_payment_collection(self, cart_id: str) -> APIResponse:
        return self.post("/payment-collections", json={"cart_id": cart_id})

    def initialize_payment_session(
        self,
        payment_collection_id: str,
        *,
        provider_id: str,
        data: dict[str, Any] | None = None,
    ) -> APIResponse:
        payload: dict[str, Any] = {"provider_id": provider_id}
        if data is not None:
            payload["data"] = data
        return self.post(
            f"/payment-collections/{payment_collection_id}/payment-sessions",
            json=payload,
        )

    def complete_cart(self, cart_id: str) -> APIResponse:
        return self.post(f"/carts/{cart_id}/complete")
