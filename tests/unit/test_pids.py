# FROZEN — DO NOT MODIFY (tests/FROZEN_MANIFEST.sha256)
"""Unit tests for tracer_diag.pids (D-013). Expected values from spike S2/S4 oracle (C-015).
Float tolerance: abs=1e-9 (exact rational formulas; only binary rounding of /255 and /4 applies)."""
import pytest
from tracer_diag.pids import decode_pid, monitor_status, supported_pids
from tracer_diag.errors import ProtocolError, UnsupportedPid

TOL = 1e-9


@pytest.mark.parametrize("pid,data,value,unit", [
    (0x0C, "1AF8", 1726.0, "rpm"), (0x0C, "0000", 0.0, "rpm"), (0x0C, "FFFF", 16383.75, "rpm"),
    (0x05, "00", -40, "degC"), (0x05, "7B", 83, "degC"), (0x05, "FF", 215, "degC"),
    (0x0F, "3C", 20, "degC"), (0x0D, "3C", 60, "km/h"), (0x0B, "65", 101, "kPa"),
    (0x11, "80", 50.19607843137255, "%"), (0x04, "FF", 100.0, "%"),
    (0x0E, "80", 0.0, "deg"), (0x42, "3200", 12.8, "V"), (0x21, "0102", 258, "km"),
    (0x1C, "03", 3, "enum"),
])
def test_T_U06_decode_pid_formulas(pid, data, value, unit):
    """T-U06 | SC-3 | C-015 | SAE J1979 scaling for every PID in PID_TABLE."""
    r = decode_pid(pid, bytes.fromhex(data))
    assert r.pid == pid and r.unit == unit
    assert r.value == pytest.approx(value, abs=TOL)


def test_T_U07_decode_pid_unknown_pid():
    """T-U07 | SC-3 | D-013 | PIDs without a decoder raise UnsupportedPid (never guessed)."""
    with pytest.raises(UnsupportedPid):
        decode_pid(0x5C, bytes.fromhex("80"))


@pytest.mark.parametrize("pid,data", [(0x0C, "1A"), (0x05, "7B00"), (0x42, "")])
def test_T_U08_decode_pid_wrong_length(pid, data):
    """T-U08 | SC-3 | D-013 | data length must equal PID_TABLE length."""
    with pytest.raises(ProtocolError):
        decode_pid(pid, bytes.fromhex(data))


@pytest.mark.parametrize("data,mil,count", [("82076504", True, 2), ("00076504", False, 0), ("83076504", True, 3)])
def test_T_U09_monitor_status(data, mil, count):
    """T-U09 | SC-2 | C-015 | MIL = bit 7 of A; DTC count = A & 0x7F."""
    st = monitor_status(bytes.fromhex(data))
    assert (st.mil, st.dtc_count) == (mil, count)


def test_T_U10_monitor_status_wrong_length():
    """T-U10 | SC-2 | D-013."""
    with pytest.raises(ProtocolError):
        monitor_status(bytes.fromhex("8207"))


def test_T_U11_supported_pids_bitmaps():
    """T-U11 | SC-3 | C-015 | spike S4 oracle: 983B8013 and BE1FA813; offsets 0x20/0x40."""
    assert supported_pids({0x00: bytes.fromhex("983B8013")}) == {
        0x01, 0x04, 0x05, 0x0B, 0x0C, 0x0D, 0x0F, 0x10, 0x11, 0x1C, 0x1F, 0x20}
    assert supported_pids({0x00: bytes.fromhex("BE1FA813")}) == {
        0x01, 0x03, 0x04, 0x05, 0x06, 0x07, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x13, 0x15, 0x1C, 0x1F, 0x20}
    assert supported_pids({0x20: bytes.fromhex("00000001"), 0x40: bytes.fromhex("40000000")}) == {0x40, 0x42}
    assert supported_pids({0x00: bytes.fromhex("00000000")}) == set()


def test_T_U12_supported_pids_bad_bitmap_length():
    """T-U12 | SC-3 | D-013."""
    with pytest.raises(ProtocolError):
        supported_pids({0x00: bytes.fromhex("983B80")})
