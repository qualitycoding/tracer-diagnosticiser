# FROZEN — DO NOT MODIFY (tests/FROZEN_MANIFEST.sha256)
"""Unit tests for tracer_diag.report (D-016)."""
from tracer_diag.report import build_report, render_text, REPORT_SCHEMA_VERSION
from tracer_diag.session import ProbeResult, VehicleInfo
from tracer_diag.pids import MonitorStatus, Reading
from tracer_diag import __version__


def _rep(now, **kw):
    probe = ProbeResult("6", "ISO 15765-4 (CAN 11/500)", 12.6, ["7E8"], False)
    info = VehicleInfo("JYARN0000M0012345", ["B7N8591A00"], None)
    return build_report(probe=probe, dtcs={"stored": {"7E8": ["P0133"]}, "pending": {"7E8": []}, "permanent": {}},
                        readings={"7E8": [Reading(0x0C, "rpm", 1726.0, "rpm")]}, info=info,
                        monitor={"7E8": MonitorStatus(True, 1)}, now=now, **kw)


def test_T_U24_report_schema(fixed_now):
    """T-U24 | SC-4 | D-016 | top-level keys, schema version, UTC timestamp, tool version."""
    r = _rep(fixed_now)
    assert set(r) == {"schema_version", "generated_at", "tool_version", "adapter", "ecus", "vehicle",
                      "monitor", "dtcs", "readings"}
    assert r["schema_version"] == REPORT_SCHEMA_VERSION == "1"
    assert r["generated_at"] == "2026-09-26T12:00:00+00:00" and r["tool_version"] == __version__
    assert r["readings"]["7E8"] == [{"pid": "0x0C", "name": "rpm", "value": 1726.0, "unit": "rpm"}]
    assert r["adapter"] == {"protocol_number": "6", "protocol_name": "ISO 15765-4 (CAN 11/500)",
                            "voltage": 12.6, "low_voltage": False}


def test_T_U25_report_vin_redaction(fixed_now):
    """T-U25 | SC-6 | D-016 | VIN redacted by default; full only when redact_vin=False."""
    assert _rep(fixed_now)["vehicle"]["vin"] == "JYA********012345"
    r = _rep(fixed_now, redact_vin=False)
    assert r["vehicle"]["vin"] == "JYARN0000M0012345" and r["vehicle"]["vin_redacted"] is False


def test_T_U26_render_text(fixed_now):
    """T-U26 | SC-2 | D-016 | human summary shows MIL state, each DTC, and empty-list wording."""
    text = render_text(_rep(fixed_now))
    assert "MIL: ON" in text and "P0133" in text and "pending: none" in text
