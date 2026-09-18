"""Fire a check and wait until every node reports.

Run with::

    python examples/02_polling.py
"""

from __future__ import annotations

import contextlib
import statistics
import sys
from typing import Any

from checkhost import CheckHost, CheckHostTimeoutError
from checkhost.regions import Continent


def _summarise(payload: Any) -> str:
    """Return a one-line summary of a node entry.

    Works with both the modern dict (with ``checks``) and the legacy list
    shape returned by some peer libraries.
    """
    if isinstance(payload, dict):
        checks = payload.get("checks") or []
        country = payload.get("countryCode", "??")
        ok = sum(1 for c in checks if isinstance(c, dict) and c.get("status") == 1)
        times = [
            c.get("connectiontime")
            for c in checks
            if isinstance(c, dict) and isinstance(c.get("connectiontime"), (int, float))
        ]
        avg = statistics.mean(times) if times else 0.0
        return f"[{country}] {ok}/{len(checks)} ok, avg {avg:.0f} ms"
    if isinstance(payload, list):
        return f"{len(payload)} probe(s)"
    return "no data"


def main() -> None:
    # Force UTF-8 stdout so node city names with diacritics print cleanly on
    # Windows consoles (which default to cp1252).
    with contextlib.suppress(AttributeError):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    with CheckHost() as ch:
        task = ch.ping(
            "8.8.8.8",
            region=[Continent.EUROPE, Continent.NORTH_AMERICA],
            repeat_checks=3,
        )
        print(f"Triggered ping task {task.uuid}")
        print(f"Live report: {task.report_url}")

        try:
            report = ch.wait_for_report(task.uuid, max_wait=30.0)
        except CheckHostTimeoutError as exc:
            print(f"Timeout while polling: {exc}")
            return

        print(f"\nReport complete? {report.is_complete}")
        print(f"Nodes reported: {len(report.completed_nodes)}/{len(report)}")
        for node in sorted(report.completed_nodes):
            print(f"  {node:<25s} {_summarise(report.nodes[node])}")


if __name__ == "__main__":
    main()
