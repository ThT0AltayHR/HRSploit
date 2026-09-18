"""Demonstrate the granular exception hierarchy.

Run with::

    python examples/05_error_handling.py
"""

from __future__ import annotations

from checkhost import (
    CheckHost,
    CheckHostBadRequestError,
    CheckHostError,
    CheckHostNetworkError,
    CheckHostRateLimitError,
    CheckHostTimeoutError,
    CheckHostValidationError,
)


def main() -> None:
    with CheckHost() as ch:
        # 1. Client-side validation runs before any HTTP request.
        try:
            ch.tcp("example.com", 70000)
        except CheckHostValidationError as exc:
            print(f"Validation: {exc}")

        # 2. Network errors surface as CheckHostNetworkError.
        bogus = CheckHost(base_url="https://this-host-does-not-resolve.invalid")
        try:
            bogus.myip()
        except CheckHostNetworkError as exc:
            print(f"Network:    {exc}")

        # 3. API errors carry status + parsed response.
        try:
            ch.report("nonexistent-uuid")
        except CheckHostBadRequestError as exc:
            print(f"BadRequest: {exc} (status={exc.status})")
        except CheckHostRateLimitError as exc:
            print(f"RateLimit:  {exc}")
        except CheckHostTimeoutError as exc:
            print(f"Timeout:    {exc}")
        except CheckHostError as exc:
            print(f"CheckHost:  {exc}")


if __name__ == "__main__":
    main()
