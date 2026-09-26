"""Mode 01/02 PID decoding (D-013)."""
from __future__ import annotations

from dataclasses import dataclass

from .errors import ProtocolError, UnsupportedPid


@dataclass(frozen=True)
class Reading:
    pid: int
    name: str
    value: float | int | bool
    unit: str


@dataclass(frozen=True)
class MonitorStatus:
    mil: bool
    dtc_count: int


# PID -> (name, unit, data length in bytes). Frozen table; formulas in D-013.
PID_TABLE: dict[int, tuple[str, str, int]] = {
    0x04: ("engine_load", "%", 1),
    0x05: ("coolant_temp", "degC", 1),
    0x0B: ("intake_map", "kPa", 1),
    0x0C: ("rpm", "rpm", 2),
    0x0D: ("speed", "km/h", 1),
    0x0E: ("timing_advance", "deg", 1),
    0x0F: ("intake_air_temp", "degC", 1),
    0x11: ("throttle_pos", "%", 1),
    0x1C: ("obd_standard", "enum", 1),
    0x21: ("distance_with_mil", "km", 2),
    0x42: ("module_voltage", "V", 2),
}

_FORMULAS = {
    0x04: lambda a, b: a * 100 / 255,
    0x05: lambda a, b: a - 40,
    0x0B: lambda a, b: a,
    0x0C: lambda a, b: (256 * a + b) / 4,
    0x0D: lambda a, b: a,
    0x0E: lambda a, b: a / 2 - 64,
    0x0F: lambda a, b: a - 40,
    0x11: lambda a, b: a * 100 / 255,
    0x1C: lambda a, b: a,
    0x21: lambda a, b: 256 * a + b,
    0x42: lambda a, b: (256 * a + b) / 1000,
}


def decode_pid(pid: int, data: bytes) -> Reading:
    """Decode the data bytes (after '41 <pid>') of a supported PID."""
    if pid not in PID_TABLE:
        raise UnsupportedPid(f"0x{pid:02X}")
    name, unit, length = PID_TABLE[pid]
    if len(data) != length:
        raise ProtocolError(data)
    a = data[0]
    b = data[1] if length > 1 else 0
    value = _FORMULAS[pid](a, b)
    return Reading(pid, name, value, unit)


def monitor_status(data: bytes) -> MonitorStatus:
    """Decode PID 0x01 (4 bytes): MIL = bit 7 of A, DTC count = A & 0x7F."""
    if len(data) != 4:
        raise ProtocolError(data)
    a = data[0]
    return MonitorStatus(mil=bool(a & 0x80), dtc_count=a & 0x7F)


def supported_pids(bitmaps: dict[int, bytes]) -> set[int]:
    """Decode 'supported PID' bitmaps (keys 0x00, 0x20, 0x40...; 4 bytes each)."""
    result: set[int] = set()
    for base, bitmap in bitmaps.items():
        if len(bitmap) != 4:
            raise ProtocolError(bitmap)
        value = int.from_bytes(bitmap, "big")
        for i in range(32):
            if value & (1 << (31 - i)):
                result.add(base + i + 1)
    return result
