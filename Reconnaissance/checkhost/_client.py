"""Stdlib-only HTTP layer for the Check-Host API.

Hand-rolled on top of :mod:`urllib.request` so the package keeps its
zero-runtime-dependency promise. Connection pooling is not implemented;
each call opens a fresh HTTPS connection. For most diagnostic workloads
that is fine because the per-call latency is dominated by node fan-out
on the API side, not by client-side handshakes.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any

from ._exceptions import (
    CheckHostAPIError,
    CheckHostNetworkError,
    exception_for_status,
)
from ._version import __version__

logger = logging.getLogger("checkhost")

DEFAULT_BASE_URL = "https://api.check-host.cc"
DEFAULT_TIMEOUT = 30.0
DEFAULT_USER_AGENT = f"check-host-python/{__version__}"

ENV_TOKEN = "CHECK_HOST_API_TOKEN"
ENV_TOKEN_LEGACY = "CHECK_HOST_API_KEY"


class Client:
    """Internal HTTP client. End users go through :class:`checkhost.CheckHost`."""

    __slots__ = ("_closed", "base_url", "timeout", "token", "user_agent")

    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        user_agent: str | None = None,
    ) -> None:
        if token is None:
            token = os.environ.get(ENV_TOKEN) or os.environ.get(ENV_TOKEN_LEGACY)
        self.token: str | None = token or None
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        self._closed = False

    def close(self) -> None:
        """Mark the client as closed. Subsequent calls raise ``RuntimeError``."""
        self._closed = True

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def _check_open(self) -> None:
        if self._closed:
            raise RuntimeError("Client has been closed")

    def _build_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def _build_headers(self, *, json_body: bool) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if json_body:
            headers["Content-Type"] = "application/json"
        if self.token:
            # Bearer header for every verb; the token never touches the URL
            # or the request body.
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _execute(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None,
        accept_binary: bool,
    ) -> tuple[int, bytes, str]:
        self._check_open()

        url = self._build_url(path)
        encoded_body: bytes | None = None
        if body is not None:
            encoded_body = json.dumps(body, separators=(",", ":")).encode("utf-8")
        headers = self._build_headers(json_body=encoded_body is not None)

        if accept_binary:
            headers["Accept"] = "image/png, */*"

        req = urllib.request.Request(
            url=url,
            data=encoded_body,
            headers=headers,
            method=method,
        )
        logger.debug(
            "check-host HTTP %s %s (body_bytes=%d)",
            method,
            url,
            len(encoded_body) if encoded_body else 0,
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                status = resp.status
                payload = resp.read()
                content_type = resp.headers.get("Content-Type", "")
        except urllib.error.HTTPError as exc:
            status = exc.code
            try:
                payload = exc.read()
            except Exception:
                payload = b""
            content_type = exc.headers.get("Content-Type", "") if exc.headers else ""
            logger.debug("check-host HTTP error %s -> %d", url, status)
            self._raise_for_status(status, payload, content_type)
            raise  # pragma: no cover - _raise_for_status always raises on non-2xx
        except urllib.error.URLError as exc:
            logger.debug("check-host network error %s: %s", url, exc)
            raise CheckHostNetworkError(
                f"Network error while contacting {url}: {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            logger.debug("check-host timeout %s", url)
            raise CheckHostNetworkError(f"Request to {url} timed out") from exc

        logger.debug("check-host HTTP %s -> %d (%d bytes)", url, status, len(payload))
        if status >= 400:
            self._raise_for_status(status, payload, content_type)
        return status, payload, content_type

    @staticmethod
    def _raise_for_status(status: int, payload: bytes, content_type: str) -> None:
        text = payload.decode("utf-8", errors="replace") if payload else ""
        parsed: dict[str, Any] | None = None
        if text and "json" in content_type.lower():
            try:
                obj = json.loads(text)
                if isinstance(obj, dict):
                    parsed = obj
            except json.JSONDecodeError:
                parsed = None

        message = text.strip() or f"HTTP {status}"
        if parsed is not None:
            for key in ("message", "error", "detail"):
                value = parsed.get(key)
                if isinstance(value, str) and value:
                    message = value
                    break

        cls = exception_for_status(status)
        raise cls(message, status=status, response=parsed, raw_body=text or None)

    def post(self, path: str, body: dict[str, Any] | None = None) -> Any:
        """Issue ``POST`` and return the parsed JSON body."""
        _status, raw, content_type = self._execute(
            "POST", path, body=body or {}, accept_binary=False
        )
        return self._decode_json(raw, content_type)

    def get(self, path: str) -> Any:
        """Issue ``GET`` and return the parsed JSON body."""
        _status, raw, content_type = self._execute("GET", path, body=None, accept_binary=False)
        return self._decode_json(raw, content_type)

    def get_bytes(self, path: str) -> bytes:
        """Issue ``GET`` and return the raw response body."""
        _status, raw, _ct = self._execute("GET", path, body=None, accept_binary=True)
        return raw

    @staticmethod
    def _decode_json(raw: bytes, content_type: str) -> Any:
        if not raw:
            return None
        text = raw.decode("utf-8", errors="replace").strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise CheckHostAPIError(
                f"Could not decode JSON response (Content-Type={content_type!r}): {exc.msg}",
                status=200,
                response=None,
                raw_body=text,
            ) from exc
