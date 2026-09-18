"""Client-side validation helpers.

Validation runs before any HTTP call so the caller gets immediate, well-typed
errors instead of opaque 400 responses from the API.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Final

from ._exceptions import CheckHostValidationError

DNS_QUERY_METHODS: Final[frozenset[str]] = frozenset(
    {
        "A/AAAA",
        "A",
        "AAAA",
        "NS",
        "MD",
        "MF",
        "CNAME",
        "SOA",
        "MB",
        "MG",
        "MR",
        "NULL",
        "WKS",
        "PTR",
        "HINFO",
        "MINFO",
        "MX",
        "TXT",
        "SRV",
        "EDNS",
        "SPF",
        "AXFR",
        "MAILB",
        "MAILA",
        "ANY",
        "CAA",
        "DNSKEY",
    }
)

MTR_PROTOCOLS: Final[frozenset[str]] = frozenset({"icmp", "udp", "tcp"})

MTR_FORCE_IP_VERSIONS: Final[frozenset[int]] = frozenset({4, 6})

MIN_PORT: Final[int] = 1
MAX_PORT: Final[int] = 65535

MIN_REPEAT_CHECKS: Final[int] = 0
MAX_REPEAT_CHECKS: Final[int] = 120

MTR_MIN_REPEAT_CHECKS: Final[int] = 3
MTR_MAX_REPEAT_CHECKS: Final[int] = 30

FULLSCAN_SCOPES: Final[frozenset[str]] = frozenset({"basic", "deep", "full"})

MAX_PREFIX_MASK: Final[int] = 128

_ASN_RE: Final[re.Pattern[str]] = re.compile(r"^(?:AS)?(\d+)$", re.IGNORECASE)
_SHA256_RE: Final[re.Pattern[str]] = re.compile(r"^[a-f0-9]{64}$")


def validate_target(target: str) -> str:
    """Ensure *target* is a non-empty string and strip surrounding whitespace."""
    if not isinstance(target, str):
        raise CheckHostValidationError(f"target must be a string, got {type(target).__name__}")
    stripped = target.strip()
    if not stripped:
        raise CheckHostValidationError("target must be a non-empty string")
    return stripped


def validate_port(port: int) -> int:
    """Ensure *port* is an int in the range [1, 65535]."""
    if isinstance(port, bool) or not isinstance(port, int):
        raise CheckHostValidationError(f"port must be an int, got {type(port).__name__}")
    if not (MIN_PORT <= port <= MAX_PORT):
        raise CheckHostValidationError(
            f"port must be between {MIN_PORT} and {MAX_PORT}, got {port}"
        )
    return port


def validate_repeat_checks(value: int, *, mtr: bool = False) -> int:
    """Validate ``repeat_checks`` against the per-endpoint limits.

    Ping/TCP/UDP/HTTP: 0-120. MTR: 3-30.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise CheckHostValidationError(f"repeat_checks must be an int, got {type(value).__name__}")
    if mtr:
        lo, hi = MTR_MIN_REPEAT_CHECKS, MTR_MAX_REPEAT_CHECKS
        kind = "MTR"
    else:
        lo, hi = MIN_REPEAT_CHECKS, MAX_REPEAT_CHECKS
        kind = "monitoring"
    if not (lo <= value <= hi):
        raise CheckHostValidationError(
            f"repeat_checks for {kind} must be between {lo} and {hi}, got {value}"
        )
    return value


def validate_dns_query_method(method: str) -> str:
    """Ensure *method* is one of the DNS record types accepted by the API.

    Accepts the special compound ``A/AAAA`` (Swagger 2.0.0 default) as
    well as the individual record types.
    """
    if not isinstance(method, str):
        raise CheckHostValidationError(
            f"query_method must be a string, got {type(method).__name__}"
        )
    stripped = method.strip()
    # Preserve "A/AAAA" verbatim; otherwise compare case-insensitively.
    normalized = stripped if stripped == "A/AAAA" else stripped.upper()
    if normalized not in DNS_QUERY_METHODS:
        raise CheckHostValidationError(
            f"query_method '{method}' is not a valid DNS record type. "
            f"Allowed: {sorted(DNS_QUERY_METHODS)}"
        )
    return normalized


def validate_mtr_force_ip_version(value: int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise CheckHostValidationError(
            f"force_ip_version must be 4 or 6, got {type(value).__name__}"
        )
    if value not in MTR_FORCE_IP_VERSIONS:
        raise CheckHostValidationError(f"force_ip_version must be 4 or 6, got {value}")
    return value


def validate_mtr_force_protocol(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise CheckHostValidationError(
            f"force_protocol must be a string, got {type(value).__name__}"
        )
    normalized = value.strip().lower()
    if normalized not in MTR_PROTOCOLS:
        raise CheckHostValidationError(
            f"force_protocol must be one of {sorted(MTR_PROTOCOLS)}, got '{value}'"
        )
    return normalized


def validate_region(region: Iterable[str] | None) -> list[str] | None:
    """Normalise a region iterable into a list of trimmed non-empty strings."""
    if region is None:
        return None
    if isinstance(region, str):
        raise CheckHostValidationError("region must be a sequence of strings, not a single string")
    out: list[str] = []
    for idx, r in enumerate(region):
        if not isinstance(r, str):
            raise CheckHostValidationError(
                f"region[{idx}] must be a string, got {type(r).__name__}"
            )
        rs = r.strip()
        if not rs:
            raise CheckHostValidationError(f"region[{idx}] is empty")
        out.append(rs)
    return out


def validate_asn(asn: int | str) -> str:
    """Normalise an AS number to its bare decimal form.

    Accepts ``13335``, ``"13335"`` and ``"AS13335"``; the API takes either
    spelling but the bare number keeps generated URLs canonical.
    """
    if isinstance(asn, bool):
        raise CheckHostValidationError("asn must be an int or string, got bool")
    if isinstance(asn, int):
        if asn < 0:
            raise CheckHostValidationError(f"asn must be >= 0, got {asn}")
        return str(asn)
    if not isinstance(asn, str):
        raise CheckHostValidationError(f"asn must be an int or string, got {type(asn).__name__}")
    match = _ASN_RE.match(asn.strip())
    if match is None:
        raise CheckHostValidationError(f"asn must look like '13335' or 'AS13335', got '{asn}'")
    return match.group(1)


def validate_cert_sha256(sha256: str) -> str:
    """Ensure *sha256* is a 64-character lowercase hex certificate fingerprint."""
    if not isinstance(sha256, str):
        raise CheckHostValidationError(f"sha256 must be a string, got {type(sha256).__name__}")
    normalized = sha256.strip().lower()
    if _SHA256_RE.match(normalized) is None:
        raise CheckHostValidationError(f"sha256 must be 64 hexadecimal characters, got '{sha256}'")
    return normalized


def validate_prefix_mask(mask: int) -> int:
    """Ensure a CIDR prefix length is in the range [0, 128]."""
    if isinstance(mask, bool) or not isinstance(mask, int):
        raise CheckHostValidationError(f"mask must be an int, got {type(mask).__name__}")
    if not (0 <= mask <= MAX_PREFIX_MASK):
        raise CheckHostValidationError(f"mask must be between 0 and {MAX_PREFIX_MASK}, got {mask}")
    return mask


def validate_fullscan_scope(scope: str) -> str:
    """Ensure *scope* is one of ``basic``, ``deep`` or ``full``."""
    if not isinstance(scope, str):
        raise CheckHostValidationError(f"scope must be a string, got {type(scope).__name__}")
    normalized = scope.strip().lower()
    if normalized not in FULLSCAN_SCOPES:
        raise CheckHostValidationError(
            f"scope must be one of {sorted(FULLSCAN_SCOPES)}, got '{scope}'"
        )
    return normalized


def validate_timeout(timeout: int | None) -> int | None:
    if timeout is None:
        return None
    if isinstance(timeout, bool) or not isinstance(timeout, int):
        raise CheckHostValidationError(f"timeout must be an int, got {type(timeout).__name__}")
    if timeout < 0:
        raise CheckHostValidationError(f"timeout must be >= 0, got {timeout}")
    return timeout
