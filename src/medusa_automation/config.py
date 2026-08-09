from __future__ import annotations

from dataclasses import dataclass
import os
from urllib.parse import urljoin


def _env_text(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    cleaned = value.strip()
    return cleaned or default


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return int(value)


@dataclass(frozen=True, slots=True)
class Credentials:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class AppConfig:
    base_url: str = "http://localhost:3000"
    login_path: str = "/app/login"
    products_path: str = "/app/products"
    product_path_template: str = "/products/{handle}"
    store_api_path: str = "/store"
    admin_api_path: str = "/admin"
    headless: bool = True
    slow_mo: int = 0
    browser: str = "chromium"
    timeout_ms: int = 15_000
    storage_state_path: str | None = None
    run_live_tests: bool = False

    @classmethod
    def from_env(cls) -> "AppConfig":
        storage_state_path = os.getenv("STORAGE_STATE_PATH", "").strip() or None
        return cls(
            base_url=_env_text("BASE_URL", cls.base_url).rstrip("/"),
            login_path=_env_text("ADMIN_LOGIN_PATH", cls.login_path),
            products_path=_env_text("PRODUCTS_PATH", cls.products_path),
            product_path_template=_env_text("PRODUCT_PATH_TEMPLATE", cls.product_path_template),
            store_api_path=_env_text("STORE_API_PATH", cls.store_api_path),
            admin_api_path=_env_text("ADMIN_API_PATH", cls.admin_api_path),
            headless=_env_bool("HEADLESS", cls.headless),
            slow_mo=_env_int("SLOW_MO", 0),
            browser=_env_text("BROWSER", cls.browser),
            timeout_ms=_env_int("TIMEOUT_MS", cls.timeout_ms),
            storage_state_path=storage_state_path,
            run_live_tests=_env_bool("RUN_E2E", cls.run_live_tests),
        )

    def build_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        return urljoin(f"{self.base_url.rstrip('/')}/", path.lstrip("/"))

    def product_url(self, handle: str) -> str:
        return self.build_url(self.product_path_template.format(handle=handle))

    def store_api_url(self, path: str = "") -> str:
        return self.build_url(f"{self.store_api_path.rstrip('/')}/{path.lstrip('/')}")

    def admin_api_url(self, path: str = "") -> str:
        return self.build_url(f"{self.admin_api_path.rstrip('/')}/{path.lstrip('/')}")
