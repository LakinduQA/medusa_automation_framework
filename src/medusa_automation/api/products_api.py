from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from playwright.sync_api import APIResponse

from medusa_automation.api.base_client import BaseApiClient


@dataclass(slots=True)
class ProductsApiClient(BaseApiClient):
    """Store and admin product operations."""

    def list_products(
        self, *, limit: int = 20, offset: int = 0, q: str | None = None
    ) -> APIResponse:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if q:
            params["q"] = q
        return self.get("/products", params=params)

    def get_product(self, product_id: str) -> APIResponse:
        return self.get(f"/products/{product_id}")

    def list_variants(self, product_id: str) -> APIResponse:
        return self.get(f"/products/{product_id}/variants")

    def list_collections(self) -> APIResponse:
        return self.get("/collections")

    def list_categories(self) -> APIResponse:
        return self.get("/product-categories")

    def admin_list_products(self, *, limit: int = 20, offset: int = 0) -> APIResponse:
        return self.get(
            "/products",
            params={"limit": limit, "offset": offset},
            admin=True,
            store=False,
        )
