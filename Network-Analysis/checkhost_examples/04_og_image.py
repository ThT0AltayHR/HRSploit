"""Trigger a check and save the dynamic status map to a PNG file.

Run with::

    python examples/04_og_image.py
"""

from __future__ import annotations

import time
from pathlib import Path

from checkhost import CheckHost
from checkhost.regions import Continent


def main() -> None:
    with CheckHost() as ch:
        task = ch.ping("1.1.1.1", region=list(Continent.ALL))
        print(f"Task {task.uuid}, waiting briefly for nodes to report ...")
        time.sleep(3.0)
        out = ch.save_og_image(task.uuid, Path("./status.png"))
        print(f"Saved status map to {out.resolve()} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
