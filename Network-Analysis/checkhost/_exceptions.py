"""Exception hierarchy for the check-host SDK."""

from __future__ import annotations

from typing import Any


class CheckHostError(Exception):
    """Base class for all errors raised by this library."""


class CheckHostNetworkError(CheckHostError):
    """Raised when the HTTP request fails for network reasons.

    Wraps the underlying ``URLError``/``OSError``. Use ``__cause__`` to access it.
    """


class CheckHostTimeoutError(CheckHostError):
    """Raised by :meth:`CheckHost.wait_for_report` when ``max_wait`` is exceeded
    and ``require_complete`` is ``True``."""


class CheckHostAPIError(CheckHostError):
    """Raised when the API returns a non-2xx status code.

    Attributes:
        status: HTTP status code returned by the API.
        response: Parsed JSON body (if any) returned by the API.
        raw_body: Raw response body text (always available).
    """

    def __init__(
        self,
        message: str,
        *,
        status: int,
        response: dict[str, Any] | None = None,
        raw_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.response = response
        self.raw_body = raw_body

    def __str__(self) -> str:
        base = super().__str__()
        return f"[HTTP {self.status}] {base}"


class CheckHostBadRequestError(CheckHostAPIError):
    """HTTP 400 - invalid payload or input parameters."""


class CheckHostNotFoundError(CheckHostAPIError):
    """HTTP 404 - resource not found (e.g. invalid UUID, missing parameter)."""


class CheckHostRateLimitError(CheckHostAPIError):
    """HTTP 429 - rate limit reached. Provide an API key or slow down."""


class CheckHostServerError(CheckHostAPIError):
    """HTTP 5xx - server-side error."""


class CheckHostValidationError(CheckHostError, ValueError):
    """Raised when client-side validation fails (e.g. invalid port, DNS type).

    Inherits from :class:`ValueError` so existing code catching ``ValueError``
    keeps working.
    """


_STATUS_TO_EXCEPTION: dict[int, type[CheckHostAPIError]] = {
    400: CheckHostBadRequestError,
    404: CheckHostNotFoundError,
    429: CheckHostRateLimitError,
    500: CheckHostServerError,
    502: CheckHostServerError,
    503: CheckHostServerError,
    504: CheckHostServerError,
}


def exception_for_status(status: int) -> type[CheckHostAPIError]:
    """Return the most specific :class:`CheckHostAPIError` subclass for *status*."""
    if status in _STATUS_TO_EXCEPTION:
        return _STATUS_TO_EXCEPTION[status]
    if 500 <= status < 600:
        return CheckHostServerError
    return CheckHostAPIError
