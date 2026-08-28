from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import APIResponse

from medusa_automation.api.base_client import BaseApiClient


@dataclass(slots=True)
class AuthApiClient(BaseApiClient):
    """Authentication endpoints for admin or store customers."""

    def login(
        self,
        email: str,
        password: str,
        actor_type: str = "user",
        provider: str = "emailpass",
    ) -> APIResponse:
        return self.post(
            f"/auth/{actor_type}/{provider}",
            json={"email": email, "password": password},
            admin=False,
            store=False,
        )

    def create_session(self, token: str) -> APIResponse:
        return self.post(
            "/auth/session",
            headers={"Authorization": f"Bearer {token}"},
            admin=False,
            store=False,
        )

    def logout(self) -> APIResponse:
        return self.delete(
            "/auth/session",
            admin=False,
            store=False,
        )

    def me(self, actor_type: str = "user") -> APIResponse:
        if actor_type == "user":
            return self.get("/users/me", admin=True, store=False)
        if actor_type == "customer":
            return self.get("/customers/me")
        raise ValueError("actor_type must be 'user' or 'customer'")

    def request_password_reset(
        self,
        email: str,
        actor_type: str = "user",
        provider: str = "emailpass",
    ) -> APIResponse:
        return self.post(
            f"/auth/{actor_type}/{provider}/reset-password",
            json={"email": email},
            admin=False,
            store=False,
        )
