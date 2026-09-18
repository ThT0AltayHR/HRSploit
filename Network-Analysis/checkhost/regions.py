"""Constants for the Check-Host API: continents, DNS record types, MTR protocols."""

from __future__ import annotations

from typing import Final


class Continent:
    """Continent codes accepted by the ``region`` field.

    Cannot be mixed with specific node identifiers in the same request.
    """

    EUROPE: Final[str] = "EU"
    NORTH_AMERICA: Final[str] = "NA"
    SOUTH_AMERICA: Final[str] = "SA"
    ASIA: Final[str] = "AS"
    AFRICA: Final[str] = "AF"
    OCEANIA: Final[str] = "OC"

    ALL: Final[tuple[str, ...]] = (
        EUROPE,
        NORTH_AMERICA,
        SOUTH_AMERICA,
        ASIA,
        AFRICA,
        OCEANIA,
    )


class DNSType:
    """DNS record types supported by the ``dns`` endpoint."""

    A_AAAA: Final[str] = "A/AAAA"
    """Combined A + AAAA query (the API default in Swagger 2.0.0)."""

    A: Final[str] = "A"
    AAAA: Final[str] = "AAAA"
    NS: Final[str] = "NS"
    MD: Final[str] = "MD"
    MF: Final[str] = "MF"
    CNAME: Final[str] = "CNAME"
    SOA: Final[str] = "SOA"
    MB: Final[str] = "MB"
    MG: Final[str] = "MG"
    MR: Final[str] = "MR"
    NULL: Final[str] = "NULL"
    WKS: Final[str] = "WKS"
    PTR: Final[str] = "PTR"
    HINFO: Final[str] = "HINFO"
    MINFO: Final[str] = "MINFO"
    MX: Final[str] = "MX"
    TXT: Final[str] = "TXT"
    SRV: Final[str] = "SRV"
    EDNS: Final[str] = "EDNS"
    SPF: Final[str] = "SPF"
    AXFR: Final[str] = "AXFR"
    MAILB: Final[str] = "MAILB"
    MAILA: Final[str] = "MAILA"
    ANY: Final[str] = "ANY"
    CAA: Final[str] = "CAA"
    DNSKEY: Final[str] = "DNSKEY"

    ALL: Final[tuple[str, ...]] = (
        A_AAAA,
        A,
        AAAA,
        NS,
        MD,
        MF,
        CNAME,
        SOA,
        MB,
        MG,
        MR,
        NULL,
        WKS,
        PTR,
        HINFO,
        MINFO,
        MX,
        TXT,
        SRV,
        EDNS,
        SPF,
        AXFR,
        MAILB,
        MAILA,
        ANY,
        CAA,
        DNSKEY,
    )


class MTRProtocol:
    """Transport protocols selectable for an MTR run via ``force_protocol``."""

    ICMP: Final[str] = "icmp"
    UDP: Final[str] = "udp"
    TCP: Final[str] = "tcp"

    ALL: Final[tuple[str, ...]] = (ICMP, UDP, TCP)


class IPVersion:
    """Convenience aliases for the MTR ``force_ip_version`` field."""

    V4: Final[int] = 4
    V6: Final[int] = 6
