from __future__ import annotations

import os
from dataclasses import dataclass

import pytest
from medusa_automation.config import AppConfig, Credentials


@dataclass(frozen=True, slots=True)
class TestContext:
    config: AppConfig
    admin_credentials: Credentials | None


def _env_flag(name: str) -> bool:
    return os.getenv(name, "false").strip().lower() in {"1", "true", "yes", "on"}


@pytest.fixture(scope="session")
def app_config() -> AppConfig:
    return AppConfig.from_env()


@pytest.fixture(scope="session")
def admin_credentials() -> Credentials | None:
    email = os.getenv("ADMIN_EMAIL", "").strip()
    password = os.getenv("ADMIN_PASSWORD", "").strip()
    if not email or not password:
        return None
    return Credentials(email=email, password=password)


@pytest.fixture(scope="session")
def live_test_context(app_config: AppConfig, admin_credentials: Credentials | None) -> TestContext:
    return TestContext(config=app_config, admin_credentials=admin_credentials)


@pytest.fixture(scope="session")
def run_live_tests() -> bool:
    return _env_flag("RUN_E2E")
