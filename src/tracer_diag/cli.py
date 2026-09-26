"""Command-line interface (D-017). Subcommands: probe, dtc, live, info, report. No write/clear commands."""
from __future__ import annotations

EXIT_OK, EXIT_USAGE, EXIT_ADAPTER, EXIT_VEHICLE, EXIT_INTERRUPTED = 0, 2, 3, 4, 130


def main(argv: list[str] | None = None, *, transport_factory=None, clock=None, sleep=None) -> int:
    """Entry point. transport_factory(port, baud, timeout) -> unopened ElmTransport-like object.
    clock() -> float seconds (used only by the live loop); sleep(seconds). See D-017."""
    raise NotImplementedError("S-008")
