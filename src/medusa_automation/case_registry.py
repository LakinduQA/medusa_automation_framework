from __future__ import annotations


def _ids(prefix: str, start: int, end: int) -> tuple[str, ...]:
    return tuple(f"TC-{prefix}-{number:03d}" for number in range(start, end + 1))


ALL_SOURCE_CASE_IDS = (
    *_ids("LGN", 1, 17),
    *_ids("PS", 1, 7),
    *_ids("PD", 1, 15),
    *_ids("CART", 1, 17),
    *_ids("CHK", 1, 30),
    "TC-CHK-31",
    *_ids("CHK", 32, 34),
)

BLOCKED_SOURCE_CASE_IDS = frozenset({"TC-PS-005"})
AUTOMATED_SOURCE_CASE_IDS = frozenset(ALL_SOURCE_CASE_IDS) - BLOCKED_SOURCE_CASE_IDS

assert len(ALL_SOURCE_CASE_IDS) == 90
assert len(AUTOMATED_SOURCE_CASE_IDS) == 89
