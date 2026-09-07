from __future__ import annotations

import os
import platform
import warnings
from pathlib import Path

import allure
import pytest

PLAYWRIGHT_TRACE_MEDIA_TYPE = "application/vnd.allure.playwright-trace"


@pytest.fixture(autouse=True)
def label_source_case(request: pytest.FixtureRequest) -> None:
    marker = request.node.get_closest_marker("source_case")
    if marker and marker.args:
        source_id = str(marker.args[0])
        allure.dynamic.label("source_case", source_id)
        allure.dynamic.tag(source_id)


def _allure_results_dir(config: pytest.Config) -> Path | None:
    results_dir = config.getoption("allure_report_dir", default=None)
    if not results_dir:
        return None
    return Path(results_dir)


def _property_value(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("\n", "\\n")


def _browser_names(config: pytest.Config) -> str:
    browsers = config.getoption("browser", default=None)
    if isinstance(browsers, (list, tuple)):
        configured_browsers = ", ".join(str(browser) for browser in browsers)
        if configured_browsers:
            return configured_browsers
    return str(browsers or os.getenv("BROWSER", "chromium"))


@pytest.hookimpl(trylast=True)
def pytest_sessionstart(session: pytest.Session) -> None:
    results_dir = _allure_results_dir(session.config)
    if results_dir is None:
        return

    results_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "Operating system": platform.platform(),
        "Python": platform.python_version(),
        "Browser": _browser_names(session.config),
        "Headless": not session.config.getoption("headed", default=False),
        "Live E2E enabled": os.getenv("RUN_E2E", "false").strip().lower()
        in {"1", "true", "yes", "on"},
    }
    optional_metadata = {
        "Git commit": os.getenv("GITHUB_SHA"),
        "CI run": os.getenv("GITHUB_RUN_ID"),
    }
    metadata.update({key: value for key, value in optional_metadata.items() if value})

    properties = "".join(
        f"{key}={_property_value(value)}{os.linesep}" for key, value in metadata.items()
    )
    (results_dir / "environment.properties").write_text(properties, encoding="utf-8")


def _attach_playwright_artifact(artifact: Path) -> None:
    if artifact.suffix.lower() == ".png":
        allure.attach.file(
            str(artifact),
            name=artifact.name,
            attachment_type=allure.attachment_type.PNG,
        )
    elif artifact.name.lower() == "trace.zip":
        allure.attach.file(
            str(artifact),
            name="Playwright trace",
            attachment_type=PLAYWRIGHT_TRACE_MEDIA_TYPE,
            extension="zip",
        )


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_teardown(
    item: pytest.Item,
    nextitem: pytest.Item | None,
):
    yield

    output_path = item.funcargs.get("output_path")
    if output_path is None:
        return

    artifacts_dir = Path(output_path)
    if not artifacts_dir.is_dir():
        return

    try:
        for artifact in sorted(artifacts_dir.iterdir()):
            if artifact.is_file():
                _attach_playwright_artifact(artifact)
    except OSError as exc:
        warnings.warn(
            f"Could not attach Playwright artifacts for {item.nodeid}: {exc}",
            pytest.PytestWarning,
            stacklevel=2,
        )
