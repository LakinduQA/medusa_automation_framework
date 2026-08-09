from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import APIResponse

from medusa_automation.api.base_client import BaseApiClient


@dataclass(slots=True)
class AuthApiClient(BaseApiClient):
    """Authentication endpoints for admin or store customers."""

    def login(self, email: str, password: str, actor_type: str = "admin") -> APIResponse:
        return self.post(
            f"/auth/{actor_type}/emailpass",
            json={"email": email, "password": password},
            admin=actor_type == "admin",
            store=actor_type != "admin",
        )

    def logout(self, actor_type: str = "admin") -> APIResponse:
        return self.delete(
            f"/auth/{actor_type}",
            admin=actor_type == "admin",
            store=actor_type != "admin",
        )

    def me(self, actor_type: str = "admin") -> APIResponse:
        return self.get(
            f"/auth/{actor_type}",
            admin=actor_type == "admin",
            store=actor_type != "admin",
        )

    def request_password_reset(self, email: str, actor_type: str = "admin") -> APIResponse:
        return self.post(
            f"/auth/{actor_type}/reset-password",
            json={"email": email},
            admin=actor_type == "admin",
            store=actor_type != "admin",
        )
