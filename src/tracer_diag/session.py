"""High-level read-only diagnostic session (D-014)."""
from __future__ import annotations
from dataclasses import dataclass, field

LOW_VOLTAGE_THRESHOLD = 12.0  # volts, engine off (D-014)


@dataclass(frozen=True)
class ProbeResult:
    protocol_number: str        # ATDPN digit(s), 'A' auto prefix stripped, e.g. '6'
    protocol_name: str          # ATDP text, 'AUTO, ' prefix stripped
    voltage: float              # ATRV volts
    ecus: list[str] = field(default_factory=list)   # headers answering 0100, sorted
    low_voltage: bool = False


@dataclass(frozen=True)
class VehicleInfo:
    vin: str | None
    calibration_ids: list[str]
    ecu_name: str | None


class DiagSession:
    def __init__(self, transport) -> None:
        raise NotImplementedError("S-006")

    def probe(self) -> ProbeResult:
        raise NotImplementedError("S-006")

    def read_dtcs(self, kind: str = "stored") -> dict[str, list[str]]:
        raise NotImplementedError("S-006")

    def read_pids(self, pids: list[int]) -> dict[str, list]:
        raise NotImplementedError("S-006")

    def read_vehicle_info(self) -> VehicleInfo:
        raise NotImplementedError("S-006")

    def read_monitor_status(self) -> dict[str, object]:
        raise NotImplementedError("S-006")

    def read_supported_pids(self) -> set[int]:
        raise NotImplementedError("S-006")
