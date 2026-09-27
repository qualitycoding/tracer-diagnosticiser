"""JSON report + text rendering (D-016)."""
from __future__ import annotations
import json  # noqa: F401  (used by write_report; tests patch report.json.dump)
import os  # noqa: F401
import tempfile  # noqa: F401

from . import __version__
from .vehicle import redact_vin as _redact_vin_str

REPORT_SCHEMA_VERSION = "1"


def _clean(text: str | None) -> str | None:
    """Strip control characters (< 0x20) and C1 characters (0x7F-0x9F) from vehicle-supplied text."""
    if text is None:
        return None
    return "".join(ch for ch in text if not (ord(ch) < 0x20 or 0x7F <= ord(ch) <= 0x9F))


def build_report(*, probe, dtcs, readings, info, monitor, now, redact_vin: bool = True) -> dict:
    vin_present = info.vin is not None
    vin_redacted = vin_present and redact_vin
    vin_out = _redact_vin_str(info.vin) if vin_redacted else info.vin

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "generated_at": now.isoformat(),
        "tool_version": __version__,
        "adapter": {
            "protocol_number": probe.protocol_number,
            "protocol_name": _clean(probe.protocol_name),
            "voltage": probe.voltage,
            "low_voltage": probe.low_voltage,
        },
        "ecus": list(probe.ecus),
        "vehicle": {
            "vin": vin_out,
            "vin_redacted": vin_redacted,
            "calibration_ids": [_clean(c) for c in info.calibration_ids],
            "ecu_name": _clean(info.ecu_name),
        },
        "monitor": {
            header: {"mil": status.mil, "dtc_count": status.dtc_count}
            for header, status in monitor.items()
        },
        "dtcs": {
            kind: dict(dtcs.get(kind, {}))
            for kind in ("stored", "pending", "permanent")
        },
        "readings": {
            header: [
                {"pid": f"0x{r.pid:02X}", "name": r.name, "value": r.value, "unit": r.unit}
                for r in readings_list
            ]
            for header, readings_list in readings.items()
        },
    }


def write_report(report: dict, path: str) -> None:
    """Atomic write: temp file in same directory, then os.replace."""
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def render_text(report: dict) -> str:
    lines = [
        f"tracer-diag {report['tool_version']}  {report['generated_at']}",
        f"Protocol: {report['adapter']['protocol_name']}  Voltage: {report['adapter']['voltage']} V",
    ]
    for header, status in report["monitor"].items():
        mil = "ON" if status["mil"] else "OFF"
        lines.append(f"ECU {header} MIL: {mil} ({status['dtc_count']} DTCs)")
    for kind in ("stored", "pending", "permanent"):
        codes = [code for codes in report["dtcs"][kind].values() for code in codes]
        lines.append(f"{kind}: " + (", ".join(codes) if codes else "none"))
    return "\n".join(lines) + "\n"
