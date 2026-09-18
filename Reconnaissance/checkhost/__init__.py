"""check-host-api - a zero-dependency Python SDK for the Check-Host.cc API.

Quickstart::

    from checkhost import CheckHost
    from checkhost.regions import Continent

    with CheckHost() as ch:
        task = ch.ping("1.1.1.1", region=[Continent.EUROPE], repeat_checks=3)
        report = ch.wait_for_report(task.uuid)
        print(report.completed_nodes)
"""

from __future__ import annotations

from ._exceptions import (
    CheckHostAPIError,
    CheckHostBadRequestError,
    CheckHostError,
    CheckHostNetworkError,
    CheckHostNotFoundError,
    CheckHostRateLimitError,
    CheckHostServerError,
    CheckHostTimeoutError,
    CheckHostValidationError,
)
from ._models import CheckCreated, FullscanJob, MinResponseINFO, Report
from ._version import __version__
from .api import CheckHost
from .regions import Continent, DNSType, IPVersion, MTRProtocol

__all__ = [
    "CheckCreated",
    "CheckHost",
    "CheckHostAPIError",
    "CheckHostBadRequestError",
    "CheckHostError",
    "CheckHostNetworkError",
    "CheckHostNotFoundError",
    "CheckHostRateLimitError",
    "CheckHostServerError",
    "CheckHostTimeoutError",
    "CheckHostValidationError",
    "Continent",
    "DNSType",
    "FullscanJob",
    "IPVersion",
    "MTRProtocol",
    "MinResponseINFO",
    "Report",
    "__version__",
]
