"""High-level :class:`CheckHost` client - the public entry point of the SDK."""

from __future__ import annotations

import logging
import time
import urllib.parse
import warnings
from collections.abc import Sequence
from pathlib import Path
from types import TracebackType
from typing import Any

from ._client import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, Client
from ._exceptions import CheckHostTimeoutError, CheckHostValidationError
from ._models import CheckCreated, FullscanJob, MinResponseINFO, Report
from ._validation import (
    validate_asn,
    validate_cert_sha256,
    validate_dns_query_method,
    validate_fullscan_scope,
    validate_mtr_force_ip_version,
    validate_mtr_force_protocol,
    validate_port,
    validate_prefix_mask,
    validate_region,
    validate_repeat_checks,
    validate_target,
    validate_timeout,
)

logger = logging.getLogger("checkhost")

_MIN_POLL_INTERVAL = 1.0


class CheckHost:
    """Synchronous client for the Check-Host.cc API.

    The token is sent as ``Authorization: Bearer <token>`` on every request.
    It is optional - without one you get anonymous access under tighter
    per-IP rate limits.

    Args:
        token: API token (UUID). Falls back to the environment variable
            ``CHECK_HOST_API_TOKEN`` (or the legacy ``CHECK_HOST_API_KEY``)
            when ``None``.
        base_url: Override the API base URL (useful for tests or dev mirrors).
        timeout: Per-request HTTP timeout in seconds.
        user_agent: Custom ``User-Agent`` header. Defaults to
            ``check-host-python/<version>``.
        apikey: Deprecated alias for *token*, kept so pre-1.1 keyword calls
            keep working.

    Example:
        >>> with CheckHost() as ch:
        ...     task = ch.ping("1.1.1.1", region=["EU"], repeat_checks=3)
        ...     report = ch.wait_for_report(task.uuid)
    """

    __slots__ = ("_client",)

    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        user_agent: str | None = None,
        apikey: str | None = None,
    ) -> None:
        if apikey is not None:
            if token is not None:
                raise CheckHostValidationError("Pass either token or apikey, not both")
            warnings.warn(
                "The 'apikey' argument is deprecated and will be removed in 2.0; "
                "use 'token' instead. The credential is now sent as an "
                "Authorization: Bearer header rather than in the request body.",
                DeprecationWarning,
                stacklevel=2,
            )
            token = apikey
        self._client = Client(
            token=token,
            base_url=base_url,
            timeout=timeout,
            user_agent=user_agent,
        )

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> CheckHost:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """Mark the underlying client as closed."""
        self._client.close()

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def myip(self) -> str:
        """Return the requesting client's public IP address (``GET /myip``)."""
        result = self._client.get("/myip")
        if isinstance(result, str):
            return result
        if isinstance(result, dict):
            for key in ("ip", "myip", "client_ip"):
                value = result.get(key)
                if isinstance(value, str):
                    return value
            return next(
                (v for v in result.values() if isinstance(v, str)),
                "",
            )
        return str(result) if result is not None else ""

    def locations(self) -> dict[str, Any]:
        """Return the full list of operational monitoring nodes (``GET /locations``).

        Returns the raw API response as a dictionary. The Check-Host API does
        not publish a schema for this endpoint; we therefore preserve every
        field instead of forcing it into a dataclass.
        """
        result = self._client.get("/locations")
        return result if isinstance(result, dict) else {}

    def info(self, target: str) -> MinResponseINFO:
        """Retrieve geolocation / ISP information for *target* (``POST /info``)."""
        target = validate_target(target)
        data = self._client.post("/info", {"target": target})
        if not isinstance(data, dict):
            raise CheckHostValidationError(f"Unexpected /info response type: {type(data).__name__}")
        return MinResponseINFO.from_json(data)

    def myinfo(self) -> MinResponseINFO:
        """Geolocation + ASN for the caller's own IP (``GET /myinfo``).

        Subject to bot detection - repeated calls without a key may yield
        a ``CheckHostRateLimitError`` carrying a captcha verification URL
        in :attr:`response`.
        """
        data = self._client.get("/myinfo")
        if not isinstance(data, dict):
            raise CheckHostValidationError(
                f"Unexpected /myinfo response type: {type(data).__name__}"
            )
        return MinResponseINFO.from_json(data)

    def whois(self, target: str) -> dict[str, Any]:
        """Run a WHOIS / RDAP lookup for *target* (``POST /whois``).

        Returns the raw API response. The shape varies by registry / RIR.
        """
        target = validate_target(target)
        data = self._client.post("/whois", {"target": target})
        return data if isinstance(data, dict) else {"raw": data}

    # ------------------------------------------------------------------
    # Monitoring
    # ------------------------------------------------------------------

    def ping(
        self,
        target: str,
        *,
        region: Sequence[str] | None = None,
        repeat_checks: int = 0,
        timeout: int | None = None,
    ) -> CheckCreated:
        """Trigger an ICMP ping check (``POST /ping``)."""
        body = self._build_monitoring_body(
            target,
            region=region,
            repeat_checks=repeat_checks,
            timeout=timeout,
        )
        return CheckCreated.from_json(self._client.post("/ping", body))

    def dns(
        self,
        target: str,
        *,
        query_method: str = "A",
        region: Sequence[str] | None = None,
        timeout: int | None = None,
    ) -> CheckCreated:
        """Trigger a DNS propagation check (``POST /dns``).

        ``timeout`` is in MILLISECONDS (100-30000); the server default is 5000.
        It was missing here while ping/tcp/udp/http all had it, even though the
        API accepts it for every check type.
        """
        body: dict[str, Any] = {
            "target": validate_target(target),
            "querymethod": validate_dns_query_method(query_method),
        }
        region_list = validate_region(region)
        if region_list is not None:
            body["region"] = region_list
        timeout_value = validate_timeout(timeout)
        if timeout_value is not None:
            body["timeout"] = timeout_value
        return CheckCreated.from_json(self._client.post("/dns", body))

    def tcp(
        self,
        target: str,
        port: int,
        *,
        region: Sequence[str] | None = None,
        repeat_checks: int = 0,
        timeout: int | None = None,
    ) -> CheckCreated:
        """Trigger a TCP handshake check (``POST /tcp``)."""
        body = self._build_monitoring_body(
            target,
            region=region,
            repeat_checks=repeat_checks,
            timeout=timeout,
        )
        body["port"] = validate_port(port)
        return CheckCreated.from_json(self._client.post("/tcp", body))

    def udp(
        self,
        target: str,
        port: int,
        *,
        payload: str | None = None,
        region: Sequence[str] | None = None,
        repeat_checks: int = 0,
        timeout: int | None = None,
    ) -> CheckCreated:
        """Trigger a UDP probe (``POST /udp``)."""
        body = self._build_monitoring_body(
            target,
            region=region,
            repeat_checks=repeat_checks,
            timeout=timeout,
        )
        body["port"] = validate_port(port)
        if payload is not None:
            if not isinstance(payload, str):
                raise CheckHostValidationError(
                    f"payload must be a string, got {type(payload).__name__}"
                )
            body["payload"] = payload
        return CheckCreated.from_json(self._client.post("/udp", body))

    def http(
        self,
        target: str,
        *,
        region: Sequence[str] | None = None,
        repeat_checks: int = 0,
        timeout: int | None = None,
    ) -> CheckCreated:
        """Trigger an HTTP performance check (``POST /http``)."""
        body = self._build_monitoring_body(
            target,
            region=region,
            repeat_checks=repeat_checks,
            timeout=timeout,
        )
        return CheckCreated.from_json(self._client.post("/http", body))

    def mtr(
        self,
        target: str,
        *,
        region: Sequence[str] | None = None,
        repeat_checks: int = 10,
        force_ip_version: int | None = None,
        force_protocol: str | None = None,
        timeout: int | None = None,
    ) -> CheckCreated:
        """Trigger an MTR (My Traceroute) diagnostic (``POST /mtr``).

        ``timeout`` is sent in MILLISECONDS (100-30000) for consistency with the
        other checks; the server converts it to whole seconds for mtr, so values
        below 1000 behave as 1000. Server default is 1000.
        """
        body: dict[str, Any] = {
            "target": validate_target(target),
            "repeatchecks": validate_repeat_checks(repeat_checks, mtr=True),
        }
        region_list = validate_region(region)
        if region_list is not None:
            body["region"] = region_list

        fiv = validate_mtr_force_ip_version(force_ip_version)
        if fiv is not None:
            body["forceIPversion"] = fiv

        fp = validate_mtr_force_protocol(force_protocol)
        if fp is not None:
            body["forceProtocol"] = fp

        timeout_value = validate_timeout(timeout)
        if timeout_value is not None:
            body["timeout"] = timeout_value

        return CheckCreated.from_json(self._client.post("/mtr", body))

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def report(self, uuid: str) -> Report:
        """Single fetch of a check's report (``GET /report/{uuid}``).

        The result may be incomplete; nodes that haven't yet reported show
        up as ``None`` values inside :attr:`Report.nodes`.
        """
        uuid = self._validate_uuid(uuid)
        data = self._client.get(f"/report/{urllib.parse.quote(uuid, safe='')}")
        if not isinstance(data, dict):
            return Report(uuid=uuid, raw={})
        return Report(uuid=uuid, raw=data)

    def wait_for_report(
        self,
        uuid: str,
        *,
        interval: float = 1.5,
        max_wait: float = 30.0,
        require_complete: bool = True,
    ) -> Report:
        """Poll ``/report/{uuid}`` until every node has reported or *max_wait* elapses.

        The poll interval is held constant (no exponential back-off). The API
        documentation recommends a minimum of one request per second per UUID;
        callers passing ``interval < 1.0`` will be clamped automatically.

        Args:
            uuid: The UUID returned by a monitoring method.
            interval: Seconds between polls (clamped to ``>= 1.0``).
            max_wait: Maximum total seconds to wait.
            require_complete: When ``True`` (default), raise
                :class:`CheckHostTimeoutError` if the timeout fires before
                every node has reported. When ``False``, return the latest
                (possibly incomplete) :class:`Report` instead.

        Returns:
            The completed :class:`Report` (or the latest one if
            ``require_complete=False``).

        Raises:
            CheckHostTimeoutError: When ``require_complete=True`` and the
                deadline elapses before completion.
        """
        uuid = self._validate_uuid(uuid)
        if max_wait < 0:
            raise CheckHostValidationError(f"max_wait must be >= 0, got {max_wait}")
        if interval <= 0:
            raise CheckHostValidationError(f"interval must be > 0, got {interval}")
        poll = max(interval, _MIN_POLL_INTERVAL)

        deadline = time.monotonic() + max_wait
        last: Report = self.report(uuid)
        if last.is_complete:
            return last
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(poll, remaining))
            last = self.report(uuid)
            if last.is_complete:
                return last
        if require_complete:
            raise CheckHostTimeoutError(
                f"Report {uuid} not complete after {max_wait}s "
                f"({len(last.completed_nodes)}/{len(last.nodes)} nodes reported)"
            )
        return last

    def og_image(self, uuid: str) -> bytes:
        """Fetch the dynamic 1200x630 PNG status map for *uuid*."""
        uuid = self._validate_uuid(uuid)
        data = self._client.get_bytes(f"/report/{urllib.parse.quote(uuid, safe='')}/og-image")
        return data

    def save_og_image(self, uuid: str, path: str | Path) -> Path:
        """Fetch :meth:`og_image` and write it to disk.

        Returns:
            The resolved path that was written.
        """
        image = self.og_image(uuid)
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(image)
        return out

    def country_map(
        self,
        uuid: str,
        *,
        format: str = "svg",
        resolution: str = "med",
    ) -> bytes:
        """Fetch the per-country world map (``GET /report/{uuid}/country-map``).

        Args:
            uuid: Report UUID returned by a monitoring method.
            format: ``"svg"`` (default) or ``"png"``.
            resolution: PNG resolution: ``"low"`` (800px), ``"med"`` (1200px),
                ``"high"`` (2000px). Ignored for SVG.

        Returns:
            Raw image bytes. SVG is UTF-8 text; PNG is binary.
        """
        uuid = self._validate_uuid(uuid)
        if format not in {"svg", "png"}:
            raise CheckHostValidationError(f"format must be 'svg' or 'png', got '{format}'")
        if resolution not in {"low", "med", "high"}:
            raise CheckHostValidationError(
                f"resolution must be one of 'low', 'med', 'high', got '{resolution}'"
            )
        query = urllib.parse.urlencode({"format": format, "res": resolution})
        path = f"/report/{urllib.parse.quote(uuid, safe='')}/country-map?{query}"
        return self._client.get_bytes(path)

    def save_country_map(
        self,
        uuid: str,
        path: str | Path,
        *,
        format: str = "svg",
        resolution: str = "med",
    ) -> Path:
        """Fetch :meth:`country_map` and write it to disk.

        Returns:
            The resolved path that was written.
        """
        data = self.country_map(uuid, format=format, resolution=resolution)
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        return out

    # ------------------------------------------------------------------
    # Network Intelligence
    # ------------------------------------------------------------------

    def ip_intel(self, ip: str) -> dict[str, Any]:
        """Full intelligence profile for a single IP (``GET /ip/{ip}``).

        Covers reverse DNS, open ports and banners, TLS certificates, BGP/ASN
        attribution, GeoIP, tech-stack, co-hosted domains, origin-leak
        candidates, threat-intel matches and honeypot activity.

        Honeypot passwords are never returned in cleartext - each entry only
        exposes ``password_captured`` and ``password_len``.

        Sections the dataset has no data for come back as empty lists or
        ``None``, so the response is returned as a plain dict rather than a
        fixed dataclass.
        """
        return self._get_intel(f"/ip/{self._q(validate_target(ip))}")

    def asn_intel(self, asn: int | str) -> dict[str, Any]:
        """Autonomous-system profile (``GET /as/{asn}``).

        Accepts ``13335`` or ``"AS13335"``. Returns prefix counts, announced
        IP totals, peers / providers / customers, IXP memberships, RPKI
        coverage, GeoIP footprint, top ports and hosted-domain summaries.
        """
        return self._get_intel(f"/as/{validate_asn(asn)}")

    def prefix_intel(self, net: str, mask: int) -> dict[str, Any]:
        """CIDR prefix intelligence (``GET /prefix/{net}/{mask}``).

        BGP origin, RPKI validity, GeoIP distribution, open-IP count, top
        ports and sample scanned hosts inside the block.
        """
        return self._get_intel(
            f"/prefix/{self._q(validate_target(net))}/{validate_prefix_mask(mask)}"
        )

    def domain_intel(self, domain: str) -> dict[str, Any]:
        """Domain intelligence (``GET /domain/{domain}``).

        Current DNS records plus passive-DNS history, TLS certificates, CT-log
        evidence, discovered subdomains, tech-stack and origin-leak
        (Cloudflare-bypass) candidates.
        """
        return self._get_intel(f"/domain/{self._q(validate_target(domain))}")

    def cert_intel(self, sha256: str) -> dict[str, Any]:
        """TLS certificate intelligence (``GET /cert/{sha256}``).

        Args:
            sha256: 64-character hex fingerprint of the certificate.

        Returns subject, issuer, SANs and validity window, every
        ``(ip, port)`` observed serving it, and matching CT-log entries.
        """
        return self._get_intel(f"/cert/{validate_cert_sha256(sha256)}")

    def port_intel(self, port: int) -> dict[str, Any]:
        """Port exposure across the scanned Internet (``GET /port/{port}``).

        Open-IP count, most common banners, top countries and ASNs,
        tech-stack and a sample of recent hosts.
        """
        return self._get_intel(f"/port/{validate_port(port)}")

    def software_intel(self, name: str, version: str | None = None) -> dict[str, Any]:
        """Tech-stack intelligence (``GET /software/{name}[/{version}]``).

        Host counts for a detected technology, version breakdown, categories
        and a sample of hosts. Pass *version* to pin the stats to one release.
        """
        path = f"/software/{self._q(validate_target(name))}"
        if version is not None:
            path += f"/{self._q(validate_target(version))}"
        return self._get_intel(path)

    def recent_scans(self, target: str) -> dict[str, Any]:
        """Most-recent fullscan jobs for *target* (``GET /scan/{target}``).

        Lets you deep-link to a fresh report instead of dispatching a
        redundant scan. Use :meth:`fullscan_jobs` for the parsed job list.
        """
        return self._get_intel(f"/scan/{self._q(validate_target(target))}")

    def fullscan_jobs(self, target: str) -> list[FullscanJob]:
        """:meth:`recent_scans` parsed into :class:`FullscanJob` objects."""
        data = self.recent_scans(target)
        scans = data.get("recent_scans")
        if not isinstance(scans, list):
            return []
        return [FullscanJob.from_json(s) for s in scans if isinstance(s, dict)]

    # ------------------------------------------------------------------
    # Fullscan
    # ------------------------------------------------------------------

    def fullscan(self, target: str, *, scope: str = "deep") -> FullscanJob:
        """Dispatch a deep multi-stage scan (``POST /fullscan``).

        Args:
            target: IPv4/IPv6 address, CIDR block, domain or AS number.
            scope: ``"basic"`` (top-100 ports + banner), ``"deep"`` (default -
                full port range, TLS, body and threat-intel) or ``"full"``
                (deep plus subdomain enumeration; domains only).

        Returns immediately with ``status="pending"``. Poll
        :meth:`fullscan_status` for progress, or use :meth:`wait_for_fullscan`.

        Anonymous CIDR submissions are capped at ``/24`` (v4) and ``/120``
        (v6); an API token raises that to ``/20`` and ``/112``.
        """
        body = {
            "target": validate_target(target),
            "scope": validate_fullscan_scope(scope),
        }
        data = self._client.post("/fullscan", body)
        if not isinstance(data, dict):
            raise CheckHostValidationError(
                f"Unexpected /fullscan response type: {type(data).__name__}"
            )
        return FullscanJob.from_json(data)

    def fullscan_status(self, uuid: str) -> FullscanJob:
        """Poll a fullscan's progress counters (``GET /fullscan/{uuid}``)."""
        uuid = self._validate_uuid(uuid)
        data = self._client.get(f"/fullscan/{self._q(uuid)}")
        if not isinstance(data, dict):
            raise CheckHostValidationError(
                f"Unexpected /fullscan/{{uuid}} response type: {type(data).__name__}"
            )
        return FullscanJob.from_json(data)

    def fullscan_results(self, uuid: str) -> dict[str, Any]:
        """Aggregated fullscan findings (``GET /fullscan/{uuid}/results``).

        Open ports, banners, DNS records, BGP context and TLS certificates.
        Partial results are available while the job is still running.
        """
        uuid = self._validate_uuid(uuid)
        data = self._client.get(f"/fullscan/{self._q(uuid)}/results")
        return data if isinstance(data, dict) else {}

    def wait_for_fullscan(
        self,
        uuid: str,
        *,
        interval: float = 3.0,
        max_wait: float = 300.0,
        require_complete: bool = True,
    ) -> FullscanJob:
        """Poll ``/fullscan/{uuid}`` until the job reaches a terminal status.

        Fullscans are far slower than node checks - a deep scan of a domain
        routinely takes minutes - so the defaults are much more patient than
        :meth:`wait_for_report`.

        Args:
            uuid: The UUID returned by :meth:`fullscan`.
            interval: Seconds between polls (clamped to ``>= 1.0``).
            max_wait: Maximum total seconds to wait.
            require_complete: When ``True`` (default), raise
                :class:`CheckHostTimeoutError` if the deadline passes while the
                job is still pending or running. When ``False``, return the
                latest job state instead.

        Raises:
            CheckHostTimeoutError: When ``require_complete=True`` and the
                deadline elapses before the job finishes.
        """
        uuid = self._validate_uuid(uuid)
        if max_wait < 0:
            raise CheckHostValidationError(f"max_wait must be >= 0, got {max_wait}")
        if interval <= 0:
            raise CheckHostValidationError(f"interval must be > 0, got {interval}")
        poll = max(interval, _MIN_POLL_INTERVAL)

        deadline = time.monotonic() + max_wait
        last = self.fullscan_status(uuid)
        if last.is_finished:
            return last
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(poll, remaining))
            last = self.fullscan_status(uuid)
            if last.is_finished:
                return last
        if require_complete:
            raise CheckHostTimeoutError(
                f"Fullscan {uuid} not finished after {max_wait}s "
                f"(status={last.status!r}, {last.subjobs_done}/{last.subjobs_total} sub-jobs)"
            )
        return last

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_intel(self, path: str) -> dict[str, Any]:
        """GET an Intelligence endpoint and normalise the envelope to a dict."""
        data = self._client.get(path)
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _q(value: str) -> str:
        """Percent-encode a single path segment."""
        return urllib.parse.quote(value, safe="")

    def _build_monitoring_body(
        self,
        target: str,
        *,
        region: Sequence[str] | None,
        repeat_checks: int,
        timeout: int | None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "target": validate_target(target),
            "repeatchecks": validate_repeat_checks(repeat_checks),
        }
        region_list = validate_region(region)
        if region_list is not None:
            body["region"] = region_list
        timeout_value = validate_timeout(timeout)
        if timeout_value is not None:
            body["timeout"] = timeout_value
        return body

    @staticmethod
    def _validate_uuid(uuid: str) -> str:
        if not isinstance(uuid, str):
            raise CheckHostValidationError(f"uuid must be a string, got {type(uuid).__name__}")
        stripped = uuid.strip()
        if not stripped:
            raise CheckHostValidationError("uuid must be a non-empty string")
        return stripped
