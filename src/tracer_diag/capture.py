"""Stretch: passive, listen-only CAN capture for module discovery (D-018). Never transmits."""
from __future__ import annotations

LISTEN_ONLY_INTERFACES = frozenset({"slcan", "virtual"})


def open_listen_only(channel: str, *, interface: str = "slcan", bitrate: int = 500000):
    """Open a python-can Bus with listen_only=True; raise UnsafeCommand for other interfaces."""
    raise NotImplementedError("S-009")


def capture(bus, duration_s: float, out_path: str, clock=None) -> int:
    """Receive frames for duration_s; write candump -L lines; return frame count."""
    raise NotImplementedError("S-009")


def summarize(log_path: str) -> dict[str, int]:
    """Count frames per arbitration ID (hex upper-case, no 0x) from a candump -L file."""
    raise NotImplementedError("S-009")
