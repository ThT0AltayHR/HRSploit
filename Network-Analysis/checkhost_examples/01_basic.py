"""Basic usage: utility endpoints + a single ping check.

Run with::

    python examples/01_basic.py
"""

from __future__ import annotations

import json

from checkhost import CheckHost


def main() -> None:
    with CheckHost() as ch:
        print("== /myip ==")
        print(ch.myip())

        print("\n== /info check-host.cc ==")
        info = ch.info("check-host.cc")
        print(f"  {info.ip} -> {info.city}, {info.country} (range {info.iprange})")

        print("\n== /locations (first 5) ==")
        locs = ch.locations()
        for i, (key, value) in enumerate(locs.items()):
            print(f"  {key}: {json.dumps(value)[:80]}")
            if i >= 4:
                break

        print("\n== ping 1.1.1.1 ==")
        task = ch.ping("1.1.1.1", region=["EU"], repeat_checks=1)
        print(f"  uuid = {task.uuid}")
        print(f"  reportURL = {task.report_url}")
        print(f"  success = {task.is_success}")


if __name__ == "__main__":
    main()
