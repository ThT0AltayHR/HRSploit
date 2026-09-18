"""Network Intelligence lookups: IP, ASN, prefix, domain, port, software.

These are passive lookups against the dataset behind the entity pages -
nothing is dispatched to the monitoring nodes, so results come back
immediately.

Run with::

    python examples/06_intelligence.py
"""

from __future__ import annotations

from typing import Any

from checkhost import CheckHost


def _section(title: str) -> None:
    print(f"\n== {title} ==")


def main() -> None:
    with CheckHost() as ch:
        _section("/ip/1.1.1.1")
        ip: dict[str, Any] = ch.ip_intel("1.1.1.1").get("data", {})
        bgp = ip.get("bgp") or {}
        geo = ip.get("geo") or {}
        print(f"  AS{bgp.get('asn')} {bgp.get('as_name')} ({bgp.get('prefix')})")
        print(f"  RPKI: {bgp.get('rpki_status')}  Geo: {geo.get('country_name')}")
        ports = ip.get("open_ports") or []
        print(f"  Open ports: {[p.get('port') for p in ports] or 'none recorded'}")

        _section("/as/AS13335")
        asn: dict[str, Any] = ch.asn_intel("AS13335").get("data", {})
        print(f"  {asn.get('as_name')} ({asn.get('as_type')}, {asn.get('country')})")
        print(f"  Prefixes: {asn.get('prefix_count')}  IXPs: {asn.get('ixp_count')}")
        print(f"  RPKI coverage: {asn.get('rpki_coverage_pct')}%")

        _section("/prefix/1.1.1.0/24")
        prefix: dict[str, Any] = ch.prefix_intel("1.1.1.0", 24).get("data", {})
        print(f"  Origin: {prefix.get('asn_name')}  Open IPs: {prefix.get('open_ips')}")

        _section("/domain/check-host.cc")
        domain: dict[str, Any] = ch.domain_intel("check-host.cc").get("data", {})
        records = domain.get("dns_records") or []
        for record in records[:5]:
            print(f"  {record.get('record_type'):<6} {record.get('value')}")
        subs = domain.get("subdomains") or []
        print(f"  Subdomains discovered: {len(subs)}")

        _section("/port/443")
        port: dict[str, Any] = ch.port_intel(443).get("data", {})
        print(f"  Open IPs worldwide: {port.get('open_ips')}")
        for server in (port.get("top_servers") or [])[:3]:
            print(f"  {server.get('server')}: {server.get('c')}")

        _section("/software/nginx")
        software: dict[str, Any] = ch.software_intel("nginx").get("data", {})
        print(f"  Hosts: {software.get('host_count')}")
        for version in (software.get("top_versions") or [])[:3]:
            print(f"  {version.get('version')}: {version.get('c')}")


if __name__ == "__main__":
    main()
