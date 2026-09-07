from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import APIResponse

from medusa_automation.api.base_client import BaseApiClient


@dataclass(slots=True)
class OrdersApiClient(BaseApiClient):
    """Order retrieval helpers."""

    def get_order(self, order_id: str) -> APIResponse:
        return self.get(f"/orders/{order_id}")

    def list_orders(self, *, limit: int = 20, offset: int = 0) -> APIResponse:
        return self.get(
            "/orders",
            params={"limit": limit, "offset": offset},
            admin=True,
            store=False,
        )
