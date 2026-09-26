"""Mode 01/02 PID decoding (D-013)."""
from __future__ import annotations
from dataclasses import dataclass


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


def decode_pid(pid: int, data: bytes) -> Reading:
    """Decode the data bytes (after '41 <pid>') of a supported PID."""
    raise NotImplementedError("S-004")


def monitor_status(data: bytes) -> MonitorStatus:
    """Decode PID 0x01 (4 bytes): MIL = bit 7 of A, DTC count = A & 0x7F."""
    raise NotImplementedError("S-004")


def supported_pids(bitmaps: dict[int, bytes]) -> set[int]:
    """Decode 'supported PID' bitmaps (keys 0x00, 0x20, 0x40...; 4 bytes each)."""
    raise NotImplementedError("S-004")
