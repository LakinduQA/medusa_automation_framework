from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Page, expect

from medusa_automation.config import AppConfig


class BasePage:
    """Shared browser actions and navigation helpers."""

    def __init__(self, page: Page, config: AppConfig) -> None:
        self.page = page
        self.config = config

    def open_path(self, path: str) -> None:
        self.page.goto(self.config.build_url(path), wait_until="domcontentloaded")

    def reload(self) -> None:
        self.page.reload(wait_until="domcontentloaded")

    def wait_for_ready(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")

    def wait_for_url(self, pattern: str) -> None:
        expect(self.page).to_have_url(re.compile(pattern))

    def take_screenshot(self, name: str) -> Path:
        artifacts_dir = Path("test-results")
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        target = artifacts_dir / f"{name}.png"
        self.page.screenshot(path=str(target), full_page=True)
        return target
