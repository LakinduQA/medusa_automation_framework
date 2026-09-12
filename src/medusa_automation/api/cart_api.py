from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from playwright.sync_api import APIResponse

from medusa_automation.api.base_client import BaseApiClient


@dataclass(slots=True)
class CartApiClient(BaseApiClient):
    """Cart lifecycle helpers."""

    def create_cart(
        self, *, region_id: str | None = None, currency_code: str | None = None
    ) -> APIResponse:
        payload: dict[str, Any] = {}
        if region_id:
            payload["region_id"] = region_id
        if currency_code:
            payload["currency_code"] = currency_code
        return self.post("/carts", json=payload)

    def get_cart(self, cart_id: str) -> APIResponse:
        return self.get(f"/carts/{cart_id}")

    def add_line_item(
        self, cart_id: str, *, variant_id: str, quantity: int = 1
    ) -> APIResponse:
        return self.post(
            f"/carts/{cart_id}/line-items",
            json={"variant_id": variant_id, "quantity": quantity},
        )

    def update_line_item(
        self, cart_id: str, line_item_id: str, *, quantity: int
    ) -> APIResponse:
        return self.post(
            f"/carts/{cart_id}/line-items/{line_item_id}", json={"quantity": quantity}
        )

    def remove_line_item(self, cart_id: str, line_item_id: str) -> APIResponse:
        return self.delete(f"/carts/{cart_id}/line-items/{line_item_id}")

    def update_cart(self, cart_id: str, **payload: Any) -> APIResponse:
        return self.post(f"/carts/{cart_id}", json=payload)
