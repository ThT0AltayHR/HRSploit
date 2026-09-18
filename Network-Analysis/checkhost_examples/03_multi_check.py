"""Run several different checks against the same target.

Run with::

    python examples/03_multi_check.py
"""

from __future__ import annotations

from checkhost import CheckHost
from checkhost.regions import Continent, DNSType, MTRProtocol

TARGET = "check-host.cc"


def main() -> None:
    with CheckHost() as ch:
        tasks = {
            "ping": ch.ping(TARGET, region=[Continent.EUROPE]),
            "http": ch.http(f"https://{TARGET}", region=[Continent.EUROPE]),
            "tcp:443": ch.tcp(TARGET, 443, region=[Continent.EUROPE]),
            "dns:NS": ch.dns(TARGET, query_method=DNSType.NS, region=[Continent.EUROPE]),
            "mtr:tcp": ch.mtr(
                TARGET,
                region=[Continent.EUROPE],
                repeat_checks=3,
                force_protocol=MTRProtocol.TCP,
            ),
        }
        for label, task in tasks.items():
            print(f"{label:<10s} -> {task.uuid} ({task.report_url})")

        print("\nWaiting for ping report...")
        ping_report = ch.wait_for_report(tasks["ping"].uuid, max_wait=20.0)
        print(f"  {len(ping_report.completed_nodes)} of {len(ping_report)} nodes")


if __name__ == "__main__":
    main()
