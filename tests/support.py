from __future__ import annotations

from collections.abc import Iterable

import pytest
from playwright.sync_api import Locator, Page, expect


def case(
    case_id: str, *values: object, partial: bool = False, resilience: bool = False
):
    marks: list[pytest.MarkDecorator] = [pytest.mark.source_case(case_id)]
    if partial:
        marks.append(pytest.mark.partial)
    if resilience:
        marks.append(pytest.mark.resilience)
    return pytest.param(*values, id=case_id, marks=marks)


def assert_no_horizontal_overflow(page: Page) -> None:
    dimensions = page.locator("body").evaluate(
        """body => ({
            bodyWidth: body.scrollWidth,
            viewportWidth: document.documentElement.clientWidth
        })"""
    )
    assert dimensions["bodyWidth"] <= dimensions["viewportWidth"] + 1, dimensions


def assert_focus_visible(locator: Locator) -> None:
    expect(locator).to_be_focused()
    style = locator.evaluate(
        """element => {
            const value = getComputedStyle(element);
            return {
                outlineStyle: value.outlineStyle,
                outlineWidth: value.outlineWidth,
                boxShadow: value.boxShadow
            };
        }"""
    )
    has_outline = style["outlineStyle"] != "none" and style["outlineWidth"] != "0px"
    has_shadow = style["boxShadow"] != "none"
    assert has_outline or has_shadow, (
        f"Focused control has no programmatic visual indicator: {style}"
    )


def assert_keyboard_reachable(page: Page, locator: Locator) -> None:
    selector = (
        "a[href], button, input, select, textarea, [tabindex]:not([tabindex='-1'])"
    )
    attempts = max(page.locator(selector).count(), 1) + 1
    for _ in range(attempts):
        if locator.evaluate("element => element === document.activeElement"):
            assert_focus_visible(locator)
            return
        page.keyboard.press("Tab")
    raise AssertionError("Control was not reachable through keyboard Tab navigation")


def visible_controls(page: Page) -> Iterable[Locator]:
    for control in page.locator(
        "a[href], button, input, select, textarea, [tabindex]:not([tabindex='-1'])"
    ).all():
        if control.is_visible() and control.is_enabled():
            yield control
