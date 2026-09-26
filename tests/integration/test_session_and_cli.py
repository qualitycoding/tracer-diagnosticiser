# FROZEN — DO NOT MODIFY (tests/FROZEN_MANIFEST.sha256)
"""Integration tests: transport + parser + decoders + session + report + CLI against FakeElm (D-012..D-017)."""
import datetime as dt, json
import pytest
from tracer_diag.transport import ElmTransport
from tracer_diag.transcript import TranscriptLog
from tracer_diag.session import DiagSession
from tracer_diag import cli
from tracer_diag.pids import MonitorStatus
from tests.fixtures.fake_elm import FakeElm, FAKE_VIN


def _session(port=None):
    t = ElmTransport(port or FakeElm())
    t.open()
    return DiagSession(t)


def test_T_I01_probe():
    """T-I01 | SC-1 | D-014, C-020 | voltage, auto-detected protocol, answering ECUs."""
    p = _session().probe()
    assert p.protocol_number == "6" and p.protocol_name == "ISO 15765-4 (CAN 11/500)"
    assert p.voltage == pytest.approx(12.6, abs=1e-9) and p.ecus == ["7E8"] and p.low_voltage is False


def test_T_I02_read_dtcs_all_kinds():
    """T-I02 | SC-2 | D-014 | stored codes decoded; empty pending; NO DATA permanent -> {}."""
    s = _session()
    assert s.read_dtcs("stored") == {"7E8": ["P0133", "P0420"]}
    assert s.read_dtcs("pending") == {"7E8": []}
    assert s.read_dtcs("permanent") == {}
    with pytest.raises(ValueError):
        s.read_dtcs("everything")


def test_T_I03_monitor_status():
    """T-I03 | SC-2 | D-014."""
    assert _session().read_monitor_status() == {"7E8": MonitorStatus(True, 2)}


def test_T_I04_read_pids_and_supported():
    """T-I04 | SC-3 | D-014 | values per ECU; supported-PID walk follows 0x20/0x40 continuation bits."""
    s = _session()
    got = {r.name: r.value for r in s.read_pids([0x0C, 0x05, 0x0D])["7E8"]}
    assert got == {"rpm": pytest.approx(1726.0), "coolant_temp": 83, "speed": 0}
    assert s.read_supported_pids() == {0x01, 0x04, 0x05, 0x0B, 0x0C, 0x0D, 0x0F, 0x10, 0x11, 0x1C, 0x1F, 0x20, 0x40, 0x42}


def test_T_I05_unsupported_pid_rejected_before_sending():
    """T-I05 | SC-3 | D-014 | UnsupportedPid raised before any bytes are written."""
    from tracer_diag.errors import UnsupportedPid
    port = FakeElm()
    s = _session(port)
    n = len(port.writes)
    with pytest.raises(UnsupportedPid):
        s.read_pids([0x0C, 0x5C])
    assert len(port.writes) == n


def test_T_I06_vehicle_info():
    """T-I06 | SC-4 | D-014 | VIN via ISO-TP multi-frame, CALID trimmed, ECU name NO DATA -> None."""
    info = _session().read_vehicle_info()
    assert info.vin == FAKE_VIN and info.calibration_ids == ["B7N8591A00"] and info.ecu_name is None


def test_T_I07_transcript_records_tx_and_rx(tmp_path):
    """T-I07 | SC-8 | D-015 | every TX and RX line logged with an ISO-8601 UTC timestamp."""
    clock = lambda: dt.datetime(2026, 9, 26, 12, 0, 0, tzinfo=dt.timezone.utc)
    path = tmp_path / "t.log"
    log = TranscriptLog(str(path), clock=clock)
    t = ElmTransport(FakeElm(), log=log)
    t.open()
    t.send("0100")
    t.close()
    log.close()
    lines = path.read_text(encoding="utf-8").splitlines()
    assert "2026-09-26T12:00:00+00:00 TX ATZ" in lines
    assert "2026-09-26T12:00:00+00:00 RX ELM327 v1.4b" in lines
    assert "2026-09-26T12:00:00+00:00 TX 0100" in lines
    assert "2026-09-26T12:00:00+00:00 RX 7E8 06 41 00 98 3B 80 13" in lines


def test_T_I08_cli_report_end_to_end(tmp_path, capsys):
    """T-I08 | SC-1..4,6 | D-016, D-017 | report subcommand writes the full JSON; VIN redacted by default."""
    out = tmp_path / "report.json"
    rc = cli.main(["--port", "COM7", "report", "--out", str(out), "--text"],
                  transport_factory=lambda port, baud, timeout: ElmTransport(FakeElm()))
    assert rc == cli.EXIT_OK
    rep = json.loads(out.read_text(encoding="utf-8"))
    assert rep["schema_version"] == "1"
    assert rep["adapter"]["protocol_number"] == "6"
    assert rep["dtcs"]["stored"] == {"7E8": ["P0133", "P0420"]}
    assert rep["monitor"]["7E8"] == {"mil": True, "dtc_count": 2}
    assert rep["vehicle"]["vin"] == "JYA********012345" and rep["vehicle"]["vin_redacted"] is True
    names = {r["name"] for r in rep["readings"]["7E8"]}
    assert {"rpm", "coolant_temp", "module_voltage"} <= names and "timing_advance" not in names
    text = capsys.readouterr().out
    assert "P0133" in text and "P0420" in text and "MIL: ON" in text


def test_T_I09_cli_show_vin_and_probe(tmp_path, capsys):
    """T-I09 | SC-1,4 | D-017 | --show-vin disables redaction; probe prints protocol and voltage."""
    f = lambda port, baud, timeout: ElmTransport(FakeElm())
    out = tmp_path / "r.json"
    assert cli.main(["--port", "COM7", "report", "--out", str(out), "--show-vin"], transport_factory=f) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["vehicle"]["vin"] == FAKE_VIN
    capsys.readouterr()
    assert cli.main(["--port", "COM7", "probe"], transport_factory=f) == 0
    text = capsys.readouterr().out
    assert "ISO 15765-4 (CAN 11/500)" in text and "12.6" in text and "7E8" in text


def test_T_I10_cli_dtc_and_info_output(capsys):
    """T-I10 | SC-2,4,6 | D-017 | 'dtc' prints one line per kind; 'info' prints VIN (redacted by default)."""
    f = lambda port, baud, timeout: ElmTransport(FakeElm())
    assert cli.main(["--port", "COM7", "dtc"], transport_factory=f) == 0
    out = capsys.readouterr().out
    assert "stored: P0133, P0420" in out and "pending: none" in out and "permanent: none" in out
    assert cli.main(["--port", "COM7", "dtc", "--kind", "stored"], transport_factory=f) == 0
    out = capsys.readouterr().out
    assert "stored: P0133, P0420" in out and "pending" not in out
    assert cli.main(["--port", "COM7", "info"], transport_factory=f) == 0
    out = capsys.readouterr().out
    assert "vin: JYA********012345" in out and "calibration_ids: B7N8591A00" in out and "ecu_name: none" in out
    assert cli.main(["--port", "COM7", "info", "--show-vin"], transport_factory=f) == 0
    assert f"vin: {FAKE_VIN}" in capsys.readouterr().out
