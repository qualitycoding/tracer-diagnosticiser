# FROZEN — DO NOT MODIFY (tests/FROZEN_MANIFEST.sha256)
"""Operational tests: configuration errors, dead adapter, ignition off, low voltage, interruption,
atomic writes, live logging cadence (D-014..D-017)."""
import csv, os
import pytest
from tracer_diag import cli, report
from tracer_diag.transport import ElmTransport, open_serial
from tracer_diag.session import DiagSession
from tracer_diag.errors import AdapterNoResponse, AdapterNotFound, LowVoltageWarning
from tests.fixtures.fake_elm import FakeElm, FakeClock


def test_T_O01_missing_port_is_usage_error(monkeypatch, capsys):
    """T-O01 | SC-5 | D-017 | no --port and no TRACER_DIAG_PORT -> exit 2 naming --port."""
    monkeypatch.delenv("TRACER_DIAG_PORT", raising=False)
    assert cli.main(["probe"]) == cli.EXIT_USAGE
    assert "--port" in capsys.readouterr().err


def test_T_O02_port_from_environment(monkeypatch):
    """T-O02 | SC-5 | D-017 | TRACER_DIAG_PORT is used when --port is absent."""
    seen = {}
    def f(port, baud, timeout):
        seen["port"] = port
        return ElmTransport(FakeElm())
    monkeypatch.setenv("TRACER_DIAG_PORT", "COM12")
    assert cli.main(["probe"], transport_factory=f) == cli.EXIT_OK
    assert seen["port"] == "COM12"


def test_T_O03_silent_adapter(capsys):
    """T-O03 | SC-5 | D-012 | no prompt -> AdapterNoResponse; CLI exit 3."""
    with pytest.raises(AdapterNoResponse):
        ElmTransport(FakeElm(silent=True)).open()
    rc = cli.main(["--port", "COM7", "probe"], transport_factory=lambda p, b, t: ElmTransport(FakeElm(silent=True)))
    assert rc == cli.EXIT_ADAPTER


def test_T_O04_open_serial_missing_device():
    """T-O04 | SC-5 | D-012 | a non-existent port -> AdapterNotFound (not a raw SerialException)."""
    with pytest.raises(AdapterNotFound):
        open_serial("COM_DOES_NOT_EXIST_987" if os.name == "nt" else "/dev/does-not-exist-987")


@pytest.mark.parametrize("answer", [["SEARCHING...", "UNABLE TO CONNECT"], ["SEARCHING...", "NO DATA"], ["CAN ERROR"]])
def test_T_O05_ignition_off_or_no_ecu(answer, capsys):
    """T-O05 | SC-5 | D-017 | vehicle silent/unreachable -> exit 4 with an ignition hint."""
    f = lambda p, b, t: ElmTransport(FakeElm(overrides={"0100": answer}))
    assert cli.main(["--port", "COM7", "probe"], transport_factory=f) == cli.EXIT_VEHICLE
    assert "ignition" in capsys.readouterr().err.lower()


def test_T_O06_low_voltage_warning():
    """T-O06 | SC-5 | D-014, R-004 | ATRV < 12.0 V -> LowVoltageWarning and flag set."""
    t = ElmTransport(FakeElm(overrides={"ATRV": ["11.6V"]}))
    t.open()
    with pytest.warns(LowVoltageWarning):
        p = DiagSession(t).probe()
    assert p.low_voltage is True


def test_T_O07_interrupt_during_live_closes_cleanly(tmp_path):
    """T-O07 | SC-5 | D-017 | Ctrl-C mid-poll: exit 130, port closed, CSV header already flushed."""
    port = FakeElm(interrupt_on="010C")
    out = tmp_path / "live.csv"
    rc = cli.main(["--port", "COM7", "live", "--pids", "0C,05", "--duration", "5", "--csv", str(out)],
                  transport_factory=lambda p, b, t: ElmTransport(port), clock=FakeClock(step=0.25), sleep=lambda s: None)
    assert rc == cli.EXIT_INTERRUPTED and port.closed
    assert out.read_text(encoding="utf-8").splitlines()[0] == "t,rpm,coolant_temp"


def test_T_O08_atomic_report_write(tmp_path, monkeypatch):
    """T-O08 | SC-4 | D-016 | a failure mid-write leaves neither the target nor a temp file."""
    target = tmp_path / "r.json"

    class DiskFull(Exception):
        pass

    def boom(*a, **k):
        raise DiskFull("disk full")
    monkeypatch.setattr(report.json, "dump", boom)
    with pytest.raises(DiskFull):
        report.write_report({"schema_version": "1"}, str(target))
    assert list(tmp_path.iterdir()) == []


def test_T_O09_live_cadence_and_rows(tmp_path):
    """T-O09 | SC-3 | D-017 | one clock read per iteration; stop when elapsed >= duration;
    sleep(interval) requested each row; 0.25 s steps over 1.0 s -> exactly 3 rows."""
    sleeps = []
    out = tmp_path / "live.csv"
    rc = cli.main(["--port", "COM7", "live", "--pids", "0C,05", "--hz", "4", "--duration", "1", "--csv", str(out)],
                  transport_factory=lambda p, b, t: ElmTransport(FakeElm()), clock=FakeClock(step=0.25),
                  sleep=sleeps.append)
    assert rc == cli.EXIT_OK
    rows = list(csv.reader(out.open(encoding="utf-8")))
    assert rows[0] == ["t", "rpm", "coolant_temp"] and len(rows) == 4
    assert rows[1][1:] == ["1726.0", "83"]
    assert sleeps == [pytest.approx(0.25)] * 3


def test_T_O10_live_rejects_unknown_pid_before_polling(tmp_path, capsys):
    """T-O10 | SC-5 | D-017 | a PID without a decoder is a usage error (exit 2); no mode-01 query sent."""
    port = FakeElm()
    rc = cli.main(["--port", "COM7", "live", "--pids", "0C,5C", "--duration", "1", "--csv", str(tmp_path / "x.csv")],
                  transport_factory=lambda p, b, t: ElmTransport(port), clock=FakeClock(step=0.25), sleep=lambda s: None)
    assert rc == cli.EXIT_USAGE
    assert not [c for c in port.commands if c.startswith("01")]
    assert "5c" in capsys.readouterr().err.lower()
