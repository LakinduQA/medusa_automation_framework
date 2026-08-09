from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from medusa_automation.config import AppConfig


@dataclass(slots=True)
class BaseApiClient:
    """Shared HTTP client for Medusa admin and store APIs."""

    config: AppConfig
    request_context: APIRequestContext
    default_timeout: int | None = None

    def __post_init__(self) -> None:
        if self.default_timeout is None:
            self.default_timeout = self.config.timeout_ms

    def build_url(self, path: str, *, admin: bool = False, store: bool = True) -> str:
        if path.startswith(("http://", "https://")):
            return path
        if admin:
            return self.config.admin_api_url(path)
        if store:
            return self.config.store_api_url(path)
        return self.config.build_url(path)

    def request(
        self,
        method: str,
        path: str,
        *,
        admin: bool = False,
        store: bool = True,
        **kwargs: Any,
    ) -> APIResponse:
        timeout = kwargs.pop("timeout", self.default_timeout)
        response = self.request_context.fetch(self.build_url(path, admin=admin, store=store), method=method.upper(), timeout=timeout, **kwargs)
        return response

    def get(self, path: str, **kwargs: Any) -> APIResponse:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> APIResponse:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> APIResponse:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> APIResponse:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> APIResponse:
        return self.request("DELETE", path, **kwargs)
