"""Stretch: passive, listen-only CAN capture for module discovery (D-018). Never transmits."""
from __future__ import annotations

import time

from .errors import UnsafeCommand

LISTEN_ONLY_INTERFACES = frozenset({"slcan", "virtual"})


class _ReceiveOnlyBus:
    def __init__(self, bus) -> None:
        self._bus = bus

    def recv(self, timeout: float | None = None):
        return self._bus.recv(timeout=timeout)

    def send(self, *args, **kwargs):
        raise UnsafeCommand("capture bus is receive-only; transmit is never permitted")

    def shutdown(self) -> None:
        self._bus.shutdown()


def open_listen_only(channel: str, *, interface: str = "slcan", bitrate: int = 500000):
    """Open a python-can Bus with listen_only=True; raise UnsafeCommand for other interfaces."""
    if interface not in LISTEN_ONLY_INTERFACES:
        raise UnsafeCommand(interface)

    import can

    if interface == "slcan":
        bus = can.Bus(interface="slcan", channel=channel, bitrate=bitrate, listen_only=True)
    else:  # "virtual"
        bus = can.Bus(interface="virtual", channel=channel)

    return _ReceiveOnlyBus(bus)


def capture(bus, duration_s: float, out_path: str, clock=None) -> int:
    """Receive frames for duration_s; write candump -L lines; return frame count."""
    clock = clock or time.monotonic
    count = 0
    start = clock()
    with open(out_path, "w", encoding="utf-8") as f:
        while clock() - start < duration_s:
            msg = bus.recv(timeout=0.05)
            if msg is None:
                continue
            arb_id = f"{msg.arbitration_id:08X}" if msg.is_extended_id else f"{msg.arbitration_id:03X}"
            data_hex = msg.data.hex().upper()
            f.write(f"({msg.timestamp:.6f}) can0 {arb_id}#{data_hex}\n")
            f.flush()
            count += 1
    return count


def summarize(log_path: str) -> dict[str, int]:
    """Count frames per arbitration ID (hex upper-case, no 0x) from a candump -L file."""
    counts: dict[str, int] = {}
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            fields = line.split()
            can_id = fields[2].split("#")[0]
            counts[can_id] = counts.get(can_id, 0) + 1
    return counts
