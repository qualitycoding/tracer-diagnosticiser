"""High-level read-only diagnostic session (D-014)."""
from __future__ import annotations
from dataclasses import dataclass, field
import warnings

from .dtc import DTC_SERVICES, parse_dtc_list
from .elm_parse import parse_response
from .errors import LowVoltageWarning, NoData, ProtocolError, UnsupportedPid
from .pids import PID_TABLE, decode_pid, monitor_status, supported_pids
from .vehicle import decode_vin

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
        self._t = transport

    def _query(self, cmd: str):
        return parse_response(self._t.send(cmd))

    def probe(self) -> ProbeResult:
        voltage_line = self._t.send("ATRV")[0].strip()
        voltage = float(voltage_line.rstrip("Vv"))

        ecus = sorted({reply.header for reply in self._query("0100")})

        dpn_line = self._t.send("ATDPN")[0].strip()
        protocol_number = dpn_line[1:] if dpn_line.startswith("A") else dpn_line

        dp_line = self._t.send("ATDP")[0].strip()
        protocol_name = dp_line[len("AUTO, "):] if dp_line.startswith("AUTO, ") else dp_line

        low_voltage = voltage < LOW_VOLTAGE_THRESHOLD
        if low_voltage:
            warnings.warn(LowVoltageWarning(f"{voltage} V"))

        return ProbeResult(protocol_number, protocol_name, voltage, ecus, low_voltage)

    def read_dtcs(self, kind: str = "stored") -> dict[str, list[str]]:
        if kind not in DTC_SERVICES:
            raise ValueError(kind)
        service = DTC_SERVICES[kind]
        try:
            replies = self._query(f"{service:02X}")
        except NoData:
            return {}
        return {reply.header: parse_dtc_list(reply.data, service) for reply in replies}

    def read_pids(self, pids: list[int]) -> dict[str, list]:
        for pid in pids:
            if pid not in PID_TABLE:
                raise UnsupportedPid(f"0x{pid:02X}")

        result: dict[str, list] = {}
        for pid in pids:
            try:
                replies = self._query(f"01{pid:02X}")
            except NoData:
                continue
            for reply in replies:
                if reply.data[:2] != bytes([0x41, pid]):
                    raise ProtocolError(reply.data)
                result.setdefault(reply.header, []).append(decode_pid(pid, reply.data[2:]))
        return result

    def read_vehicle_info(self) -> VehicleInfo:
        try:
            vin = decode_vin(self._query("0902")[0].data)
        except NoData:
            vin = None

        calibration_ids: list[str] = []
        try:
            data = self._query("0904")[0].data[3:]
            for i in range(0, len(data), 16):
                chunk = data[i:i + 16].rstrip(b"\x00")
                calibration_ids.append(chunk.decode("ascii", errors="replace"))
        except NoData:
            pass

        try:
            ecu_name_data = self._query("090A")[0].data[3:]
            ecu_name = ecu_name_data.rstrip(b"\x00").decode("ascii", errors="replace")
        except NoData:
            ecu_name = None

        return VehicleInfo(vin, calibration_ids, ecu_name)

    def read_monitor_status(self) -> dict[str, object]:
        return {reply.header: monitor_status(reply.data[2:]) for reply in self._query("0101")}

    def read_supported_pids(self) -> set[int]:
        result: set[int] = set()
        base = 0x00
        while True:
            try:
                replies = self._query(f"01{base:02X}")
            except NoData:
                break
            for reply in replies:
                result |= supported_pids({base: reply.data[2:6]})
            next_base = base + 0x20
            if next_base in result and base < 0xE0:
                base = next_base
            else:
                break
        return result
