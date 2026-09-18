"""Fullscan: dispatch a deep multi-stage scan, poll it, read the findings.

A fullscan fans out typed sub-jobs (resolve / portscan / banner /
body-fetch / threat-intel) and aggregates the results. It is much slower
than a node check - budget minutes, not seconds.

Run with::

    python examples/07_fullscan.py [target]
"""

from __future__ import annotations

import sys

from checkhost import CheckHost, CheckHostTimeoutError


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "check-host.cc"

    with CheckHost() as ch:
        # Reuse a recent scan instead of burning quota on a redundant one.
        for prior in ch.fullscan_jobs(target):
            if prior.is_finished:
                print(f"Reusing finished scan {prior.uuid} from {prior.created_at}")
                _print_results(ch, prior.uuid)
                return

        print(f"Dispatching a deep fullscan of {target} ...")
        job = ch.fullscan(target, scope="deep")
        print(f"  uuid:   {job.uuid}")
        print(f"  type:   {job.target_type}")
        print(f"  status: {job.status}")
        print(f"  report: {job.report_url}")

        try:
            job = ch.wait_for_fullscan(job.uuid, interval=5.0, max_wait=300.0)
        except CheckHostTimeoutError as exc:
            print(f"\nStill running after the deadline: {exc}")
            print("Partial results below - poll again later for the rest.")
        else:
            print(f"\nFinished: {job.status} ({job.subjobs_done}/{job.subjobs_total} sub-jobs)")
            if job.subjobs_failed:
                print(f"  {job.subjobs_failed} sub-job(s) failed")

        _print_results(ch, job.uuid)


def _print_results(ch: CheckHost, uuid: str) -> None:
    data = ch.fullscan_results(uuid).get("data", {})

    ports = data.get("open_ports") or []
    print(f"\n== Open ports ({len(ports)}) ==")
    for entry in ports[:15]:
        print(f"  {entry.get('port')}/{entry.get('proto')} {entry.get('service') or ''}")

    banners = data.get("banners") or []
    print(f"\n== Banners ({len(banners)}) ==")
    for entry in banners[:10]:
        print(f"  {entry.get('port')}: {entry.get('server_str')}")

    certs = data.get("tls_certs") or []
    print(f"\n== TLS certificates ({len(certs)}) ==")
    for entry in certs[:5]:
        print(f"  {entry.get('port')}: {entry.get('subject')}")

    bgp = data.get("bgp") or {}
    if bgp:
        print(f"\n== BGP ==\n  AS{bgp.get('asn')} {bgp.get('as_name')} ({bgp.get('prefix')})")


if __name__ == "__main__":
    main()
