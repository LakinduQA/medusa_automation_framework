from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from medusa_automation.case_registry import (
    AUTOMATED_SOURCE_CASE_IDS,
    BLOCKED_SOURCE_CASE_IDS,
)

pytest_plugins = [
    "medusa_automation.fixtures.app",
    "medusa_automation.fixtures.browser",
    "medusa_automation.fixtures.api",
    "medusa_automation.fixtures.storefront",
    "medusa_automation.reporting",
]


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Fail collection if an approved source case loses executable traceability."""

    observed: dict[str, list[str]] = {}
    for item in items:
        for marker in item.iter_markers("source_case"):
            if len(marker.args) != 1 or not isinstance(marker.args[0], str):
                raise pytest.UsageError(
                    f"{item.nodeid}: source_case requires exactly one case ID"
                )
            observed.setdefault(marker.args[0], []).append(item.nodeid)

    if not observed:
        return

    config = items[0].config
    targeted_path = any("::" in arg or Path(arg).suffix == ".py" for arg in config.args)
    filtered = bool(config.option.keyword or config.option.markexpr)
    enforce_complete_portfolio = not targeted_path and not filtered

    unknown = set(observed) - AUTOMATED_SOURCE_CASE_IDS
    missing = (
        AUTOMATED_SOURCE_CASE_IDS - set(observed)
        if enforce_complete_portfolio
        else set()
    )
    duplicates = {
        case_id: nodes for case_id, nodes in observed.items() if len(nodes) != 1
    }
    blocked = set(observed) & BLOCKED_SOURCE_CASE_IDS
    if unknown or missing or duplicates or blocked:
        raise pytest.UsageError(
            "Source-case coverage mismatch: "
            f"missing={sorted(missing)}, unknown={sorted(unknown)}, "
            f"blocked={sorted(blocked)}, duplicates={duplicates}"
        )
