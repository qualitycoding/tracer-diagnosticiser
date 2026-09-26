# FROZEN — DO NOT MODIFY (tests/FROZEN_MANIFEST.sha256)
"""Security tests for the CLI surface, report sanitisation and passive capture (D-016..D-018)."""
import io, contextlib, json
import pytest
import can
from tracer_diag import cli, capture
from tracer_diag.errors import UnsafeCommand
from tracer_diag.report import build_report
from tracer_diag.session import ProbeResult, VehicleInfo
from tracer_diag.pids import MonitorStatus


@pytest.mark.parametrize("argv", [["clear"], ["erase"], ["dtc", "--clear"], ["reset"], ["write"], ["flash"]])
def test_T_S08_cli_has_no_mutating_commands(argv):
    """T-S08 | SC-6 | D-017, A-005 | argparse rejects clear/erase/reset/write/flash -> exit 2."""
    assert cli.main(["--port", "COM9"] + argv, transport_factory=lambda p, b, t: None) == cli.EXIT_USAGE


def test_T_S09_help_does_not_advertise_mutation():
    """T-S09 | SC-6 | D-017 | top-level help exits 0 and never mentions clearing/erasing."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cli.main(["--help"])
    assert rc == cli.EXIT_OK
    text = buf.getvalue().lower()
    assert "probe" in text and "report" in text
    for word in ("clear", "erase", "flash", "reset"):
        assert word not in text


def test_T_S10_report_strips_control_characters(fixed_now):
    """T-S10 | SC-4 | D-016 | ECU-supplied strings cannot inject terminal escapes into reports."""
    probe = ProbeResult("6", "ISO 15765-4 (CAN 11/500)", 12.6, ["7E8"], False)
    info = VehicleInfo("JYARN0000M0012345", ["B7N\x1b[31m8591A00"], "ECM\x1b]0;pwn\x07-ENGINE\x7f")
    rep = build_report(probe=probe, dtcs={"stored": {}, "pending": {}, "permanent": {}}, readings={},
                       info=info, monitor={"7E8": MonitorStatus(False, 0)}, now=fixed_now)
    blob = json.dumps(rep)
    assert "\u001b" not in blob and "\u0007" not in blob and "\u007f" not in blob
    assert rep["vehicle"]["ecu_name"] == "ECM]0;pwn-ENGINE"


def test_T_S11_capture_refuses_interfaces_without_listen_only():
    """T-S11 | SC-7 | D-018, R-014 | only slcan (listen_only) and virtual are allowed."""
    for iface in ("socketcan", "pcan", "kvaser", "gs_usb", "serial"):
        with pytest.raises(UnsafeCommand):
            capture.open_listen_only("can0", interface=iface)


def test_T_S12_capture_opens_slcan_listen_only_and_never_sends(monkeypatch):
    """T-S12 | SC-7 | D-018 | slcan opened with listen_only=True; the returned bus refuses send()."""
    seen = {}

    class DummyBus:
        def send(self, msg, timeout=None):
            raise AssertionError("real send reached")
        def recv(self, timeout=None):
            return None
        def shutdown(self):
            pass

    def fake_bus(**kwargs):
        seen.update(kwargs)
        return DummyBus()

    monkeypatch.setattr(can, "Bus", fake_bus)
    bus = capture.open_listen_only("COM7", interface="slcan", bitrate=500000)
    assert seen.get("interface") == "slcan" and seen.get("listen_only") is True and seen.get("bitrate") == 500000
    with pytest.raises(UnsafeCommand):
        bus.send(can.Message(arbitration_id=0x7DF, data=b"\x02\x01\x00"))
