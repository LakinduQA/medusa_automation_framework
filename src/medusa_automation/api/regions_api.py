from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import APIResponse

from medusa_automation.api.base_client import BaseApiClient


@dataclass(slots=True)
class RegionsApiClient(BaseApiClient):
    """Region and fulfillment helpers."""

    def list_regions(self) -> APIResponse:
        return self.get("/regions")

    def get_region(self, region_id: str) -> APIResponse:
        return self.get(f"/regions/{region_id}")
