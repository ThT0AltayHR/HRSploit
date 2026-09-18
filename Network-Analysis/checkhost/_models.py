"""Typed response models for the check-host API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True, kw_only=True)
class MinResponseINFO:
    """Geolocation / ISP / privacy / abuse data for a host or IP.

    Returned by :meth:`CheckHost.info` and :meth:`CheckHost.myinfo`
    (``POST /info`` and ``GET /myinfo``).

    Aligned with Swagger 2.0.0. Backwards-compatible fields ``iprange`` and
    ``zipcode`` are kept (they fall back to ``postal_code`` / empty when the
    new schema doesn't supply them) so existing callers keep working.
    """

    ip: str
    reverse: str
    country: str
    country_code: str
    is_eu: bool
    city: str
    continent: str
    latitude: float | None
    longitude: float | None
    time_zone: str
    postal_code: str
    subdivision: str
    currency_code: str
    calling_code: str
    privacy: dict[str, Any]
    asn: dict[str, Any]
    company: dict[str, Any]
    abuse: dict[str, Any]
    success: bool
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    # ── Back-compat helpers ────────────────────────────────────────────
    @property
    def zipcode(self) -> str:
        """Alias for :attr:`postal_code` (Swagger 1.2.0 compatibility)."""
        return self.postal_code

    @property
    def iprange(self) -> str:
        """Empty under Swagger 2.0.0; field removed from the API response."""
        return str(self.raw.get("iprange", ""))

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> MinResponseINFO:
        def _num(v: Any) -> float | None:
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return float(v)
            return None

        def _str(v: Any) -> str:
            return "" if v is None else str(v)

        def _dict(v: Any) -> dict[str, Any]:
            return dict(v) if isinstance(v, dict) else {}

        return cls(
            ip=_str(data.get("ip", "")),
            reverse=_str(data.get("reverse", "")),
            country=_str(data.get("country", "")),
            country_code=_str(data.get("countryCode", "")),
            is_eu=bool(data.get("isEu", False)),
            city=_str(data.get("city", "")),
            continent=_str(data.get("continent", "")),
            latitude=_num(data.get("latitude")),
            longitude=_num(data.get("longitude")),
            time_zone=_str(data.get("timeZone", "")),
            postal_code=_str(data.get("postalCode", data.get("zipcode", ""))),
            subdivision=_str(data.get("subdivision", "")),
            currency_code=_str(data.get("currencyCode", "")),
            calling_code=_str(data.get("callingCode", "")),
            privacy=_dict(data.get("privacy")),
            asn=_dict(data.get("asn")),
            company=_dict(data.get("company")),
            abuse=_dict(data.get("abuse")),
            success=bool(data.get("success", True)),
            raw=dict(data),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class CheckCreated:
    """Response object returned by every monitoring endpoint (``ping``,
    ``dns``, ``tcp``, ``udp``, ``http``, ``mtr``).

    The ``uuid`` field is the handle for subsequent ``report()`` /
    ``og_image()`` / ``country_map()`` calls. Aligned with Swagger 2.0.0:
    the live API also echoes back ``region``, ``port``, ``query``,
    ``payload`` and exposes ``og-imageURL`` on every dispatch.
    """

    status: int
    target: str
    method: str
    repeat_checks: int
    region: list[str]
    uuid: str
    report_url: str
    api_url: str
    og_image_url: str
    autodelete: str
    message: str
    success: str
    port: int | None
    query: str | None
    payload: str | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def is_success(self) -> bool:
        """``True`` if the API marked the submission as successful.

        Handles both the original Swagger spec (``"success": "success"``) and
        the current production shape (``"success": true``).
        """
        return self.success.lower() in {"success", "true", "ok"}

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> CheckCreated:
        raw_success = data.get("success", "")
        if isinstance(raw_success, bool):
            success_str = "success" if raw_success else "failure"
        else:
            success_str = str(raw_success)

        region_raw = data.get("region")
        region = [str(r) for r in region_raw] if isinstance(region_raw, list) else []

        def _optstr(v: Any) -> str | None:
            return None if v is None else str(v)

        def _optint(v: Any) -> int | None:
            if v is None or isinstance(v, bool):
                return None
            try:
                return int(v)
            except (TypeError, ValueError):
                return None

        return cls(
            status=int(data.get("status", 0)),
            target=str(data.get("target", "")),
            method=str(data.get("method", "")),
            repeat_checks=int(data.get("repeatchecks", 0)),
            region=region,
            uuid=str(data.get("uuid", "")),
            report_url=str(data.get("reportURL", "")),
            api_url=str(data.get("apiURL", "")),
            og_image_url=str(data.get("og-imageURL", "")),
            autodelete=str(data.get("autodelete", "")),
            message=str(data.get("message", "")),
            success=success_str,
            port=_optint(data.get("port")),
            query=_optstr(data.get("query")),
            payload=_optstr(data.get("payload")),
            raw=dict(data),
        )


_FULLSCAN_TERMINAL_STATUSES: frozenset[str] = frozenset({"complete", "partial", "failed"})


@dataclass(frozen=True, slots=True, kw_only=True)
class FullscanJob:
    """Master job row for a fullscan (``POST /fullscan``, ``GET /fullscan/{uuid}``).

    Also the shape of every entry in ``recent_scans()``. Progress is tracked
    through the ``subjobs_*`` counters; :attr:`is_finished` tells you when
    polling can stop.
    """

    uuid: str
    target: str
    target_type: str
    scope: str
    status: str
    subjobs_total: int
    subjobs_done: int
    subjobs_failed: int
    error: str | None
    created_at: str | None
    completed_at: str | None
    report_url: str
    api_url: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def is_finished(self) -> bool:
        """``True`` once the job reached a terminal status."""
        return self.status.lower() in _FULLSCAN_TERMINAL_STATUSES

    @property
    def progress(self) -> float:
        """Completion ratio in ``[0.0, 1.0]``. ``0.0`` while still fanning out."""
        if self.subjobs_total <= 0:
            return 0.0
        return min(1.0, self.subjobs_done / self.subjobs_total)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> FullscanJob:
        # GET /fullscan/{uuid} wraps the row in {"success": ..., "job": {...}}.
        nested = data.get("job")
        job: dict[str, Any] = nested if isinstance(nested, dict) else data

        def _optstr(v: Any) -> str | None:
            return None if v is None else str(v)

        def _int(v: Any) -> int:
            if v is None or isinstance(v, bool):
                return 0
            try:
                return int(v)
            except (TypeError, ValueError):
                return 0

        return cls(
            uuid=str(job.get("uuid", "")),
            target=str(job.get("target", "")),
            target_type=str(job.get("target_type", "")),
            scope=str(job.get("scope", "")),
            status=str(job.get("status", "")),
            subjobs_total=_int(job.get("subjobs_total")),
            subjobs_done=_int(job.get("subjobs_done")),
            subjobs_failed=_int(job.get("subjobs_failed")),
            error=_optstr(job.get("error")),
            created_at=_optstr(job.get("created_at")),
            completed_at=_optstr(job.get("completed_at")),
            report_url=str(job.get("report_url", "")),
            api_url=str(job.get("api_url", "")),
            raw=dict(job),
        )


_REPORT_META_KEYS: frozenset[str] = frozenset(
    {
        "status",
        "success",
        "target",
        "method",
        "query",
        "repeatchecks",
        "created_at",
        "delete_at",
        "payload",
        "data",
        "ok",
        "request_id",
        "metadata",
    }
)


@dataclass(frozen=True, slots=True, kw_only=True)
class Report:
    """Result wrapper for ``GET /report/{uuid}``.

    The production Check-Host API nests node results under a ``data`` field
    where each value is a dict containing node metadata plus a ``checks``
    list. Older docs (and some peer libraries) describe a flat ``{node:
    [results]}`` shape; we support both transparently.

    The raw response is always preserved via :attr:`raw` so callers can read
    fields the SDK doesn't surface explicitly (e.g. ``created_at``,
    ``delete_at``, custom ``payload`` echoes).
    """

    uuid: str
    raw: dict[str, Any]

    @property
    def nodes(self) -> dict[str, Any]:
        """Node id -> per-node payload.

        - Modern API: returns ``raw["data"]`` directly. Each value is a dict
          of node metadata (continent, country, ISP, ...) with a ``checks``
          array containing the probe results.
        - Legacy API: returns top-level keys whose value is a list or
          ``None`` (the "node hasn't reported yet" sentinel), with known
          meta keys filtered out.
        """
        data = self.raw.get("data")
        if isinstance(data, dict):
            return dict(data)
        return {
            k: v
            for k, v in self.raw.items()
            if k not in _REPORT_META_KEYS and (v is None or isinstance(v, list))
        }

    @staticmethod
    def _node_has_results(value: Any) -> bool:
        """A node is considered complete when it has at least one probe result.

        Handles both shapes:
        - dict with non-empty ``checks`` list (modern)
        - non-empty list at the top level (legacy)
        """
        if value is None:
            return False
        if isinstance(value, list):
            return len(value) > 0
        if isinstance(value, dict):
            checks = value.get("checks")
            return isinstance(checks, list) and len(checks) > 0
        return False

    @property
    def is_complete(self) -> bool:
        """``True`` iff at least one node is present and every node has
        reported probe results."""
        nodes = self.nodes
        return bool(nodes) and all(self._node_has_results(v) for v in nodes.values())

    @property
    def completed_nodes(self) -> dict[str, Any]:
        """Subset of :attr:`nodes` that have at least one probe result."""
        return {k: v for k, v in self.nodes.items() if self._node_has_results(v)}

    @property
    def pending_nodes(self) -> list[str]:
        """Node ids assigned to this check but still missing probe results."""
        return [k for k, v in self.nodes.items() if not self._node_has_results(v)]

    @property
    def status(self) -> int:
        """HTTP-status-like integer the API echoes in the body (0 if absent)."""
        v = self.raw.get("status")
        return int(v) if isinstance(v, int) else 0

    @property
    def method(self) -> str:
        """The check method the report belongs to (``ping``, ``mtr`` ...)."""
        return str(self.raw.get("method", ""))

    @property
    def target(self) -> str:
        """Target host/IP that was checked."""
        return str(self.raw.get("target", ""))

    def __len__(self) -> int:
        """Number of nodes assigned to this check."""
        return len(self.nodes)

    def __bool__(self) -> bool:
        return bool(self.nodes)
