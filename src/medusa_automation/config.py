from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urljoin

from dotenv import load_dotenv

load_dotenv()


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
    backend_base_url: str | None = None
    storefront_base_url: str | None = None
    admin_base_url: str | None = None
    login_path: str = "/app"
    products_path: str = "/app/products"
    storefront_home_path: str = "/"
    customer_login_path: str = "/account"
    customer_account_path: str = "/account"
    product_listing_path: str = "/store"
    product_path_template: str = "/products/{handle}"
    cart_path: str = "/cart"
    checkout_path: str = "/checkout"
    store_api_path: str = "/store"
    admin_api_path: str = "/admin"
    publishable_api_key: str | None = None
    headless: bool = True
    slow_mo: int = 0
    browser: str = "chromium"
    timeout_ms: int = 15_000
    storage_state_path: str | None = None
    ignore_https_errors: bool = False
    run_live_tests: bool = False

    @classmethod
    def from_env(cls) -> AppConfig:
        defaults = cls()
        base_url = _env_text("BASE_URL", defaults.base_url).rstrip("/")
        storage_state_path = os.getenv("STORAGE_STATE_PATH", "").strip() or None
        return cls(
            base_url=base_url,
            backend_base_url=_env_text("BACKEND_URL", base_url).rstrip("/"),
            storefront_base_url=_env_text("STOREFRONT_URL", base_url).rstrip("/"),
            admin_base_url=_env_text("ADMIN_URL", base_url).rstrip("/"),
            login_path=_env_text("ADMIN_LOGIN_PATH", defaults.login_path),
            products_path=_env_text("PRODUCTS_PATH", defaults.products_path),
            storefront_home_path=_env_text(
                "STOREFONT_HOME_PATH", defaults.storefront_home_path
            ),
            customer_login_path=_env_text(
                "CUSTOMER_LOGIN_PATH", defaults.customer_login_path
            ),
            customer_account_path=_env_text(
                "CUSTOMER_ACCOUNT_PATH", defaults.customer_account_path
            ),
            product_listing_path=_env_text(
                "PRODUCT_LISTING_PATH", defaults.product_listing_path
            ),
            product_path_template=_env_text(
                "PRODUCT_PATH_TEMPLATE", defaults.product_path_template
            ),
            cart_path=_env_text("CART_PATH", defaults.cart_path),
            checkout_path=_env_text("CHECKOUT_PATH", defaults.checkout_path),
            store_api_path=_env_text("STORE_API_PATH", defaults.store_api_path),
            admin_api_path=_env_text("ADMIN_API_PATH", defaults.admin_api_path),
            publishable_api_key=os.getenv("PUBLISHABLE_API_KEY", "").strip() or None,
            headless=_env_bool("HEADLESS", defaults.headless),
            slow_mo=_env_int("SLOW_MO", 0),
            browser=_env_text("BROWSER", defaults.browser),
            timeout_ms=_env_int("TIMEOUT_MS", defaults.timeout_ms),
            storage_state_path=storage_state_path,
            ignore_https_errors=_env_bool(
                "IGNORE_HTTPS_ERRORS", defaults.ignore_https_errors
            ),
            run_live_tests=_env_bool("RUN_E2E", defaults.run_live_tests),
        )

    @staticmethod
    def _join(base_url: str, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        return urljoin(f"{base_url.rstrip('/')}/", path.lstrip("/"))

    def build_url(self, path: str) -> str:
        return self._join(self.base_url, path)

    def storefront_url(self, path: str = "") -> str:
        return self._join(self.storefront_base_url or self.base_url, path)

    def admin_url(self, path: str = "") -> str:
        return self._join(self.admin_base_url or self.base_url, path)

    def backend_url(self, path: str = "") -> str:
        return self._join(self.backend_base_url or self.base_url, path)

    def product_url(self, handle: str) -> str:
        return self.storefront_url(self.product_path_template.format(handle=handle))

    def store_api_url(self, path: str = "") -> str:
        return self.backend_url(f"{self.store_api_path.rstrip('/')}/{path.lstrip('/')}")

    def admin_api_url(self, path: str = "") -> str:
        return self.backend_url(f"{self.admin_api_path.rstrip('/')}/{path.lstrip('/')}")

    def auth_api_url(self, path: str = "") -> str:
        return self.backend_url(path)
