# FROZEN — DO NOT MODIFY (tests/FROZEN_MANIFEST.sha256)
"""Security tests: the read-only allowlist (D-011) and its enforcement points (A-005 read-only)."""
import re
import pytest
from tracer_diag.safety import check_command
from tracer_diag.errors import UnsafeCommand
from tracer_diag.transport import ElmTransport
from tests.fixtures.fake_elm import FakeElm


@pytest.mark.parametrize("cmd,canon", [
    ("0100", "0100"), ("01 0c", "010C"), ("03", "03"), ("07", "07"), ("0A", "0A"), ("09 02", "0902"),
    ("02 0C 00", "020C00"), ("0600", "0600"), ("at z", "ATZ"), ("ATRV", "ATRV"), ("ATDPN", "ATDPN"),
    ("ATDP", "ATDP"), ("ATSP0", "ATSP0"), ("ATSP6", "ATSP6"), ("ATE0", "ATE0"), ("ATL0", "ATL0"),
    ("ATS1", "ATS1"), ("ATH1", "ATH1"), ("ATI", "ATI"), ("ATSH7E0", "ATSH7E0"), ("ATSH DA F1 10", "ATSHDAF110"),
    ("ATST96", "ATST96"), ("STI", "STI"), ("STDI", "STDI"), ("\t01\t05 ", "0105"),
])
def test_T_S01_allowed_commands_are_canonicalised(cmd, canon):
    """T-S01 | SC-6 | D-011 | read services and inert AT/ST commands pass; whitespace removed, upper-cased."""
    assert check_command(cmd) == canon


@pytest.mark.parametrize("cmd", ["04", "08", "0801", "05", "10 03", "11 01", "14 FF FF FF", "27 01", "2E F1 90 00",
                                 "2F 01 00", "31 01 FF 00", "34 00", "36 01", "37", "3D 14", "28 00", "85 02",
                                 "3E 00", "19 02 FF", "22 F1 90"])
def test_T_S02_mutating_and_session_services_refused(cmd):
    """T-S02 | SC-6 | D-011, R-003 | clear (04), control (08), all UDS writes/sessions/resets refused;
    UDS reads refused unless uds_read=True."""
    with pytest.raises(UnsafeCommand):
        check_command(cmd)


@pytest.mark.parametrize("cmd", ["01 0C\rATZ", "010C\n04", "01 0C;04", ">", "01>", "0", "0G", "", "   ",
                                 "01" * 17, "01\x0004", "ATZ\r"])
def test_T_S03_injection_and_malformed_refused(cmd):
    """T-S03 | SC-6 | D-011 | control chars, prompt char, odd/non-hex, empty, > MAX_COMMAND_LEN refused."""
    with pytest.raises(UnsafeCommand):
        check_command(cmd)


@pytest.mark.parametrize("cmd", ["ATMA", "ATPP 0C SV 23", "ATPPS", "ATSD 00", "ATWM 81 10 F1 3E", "ATBD", "ATSW 92",
                                 "ATSP A6", "ATSH 7E", "ATSH 7E0F", "STPX H:7E0, D:04", "STMA", "ATCRA 7E8", "AT@3 X"])
def test_T_S04_unlisted_at_and_st_commands_refused(cmd):
    """T-S04 | SC-6 | D-011 | AT/ST default-deny: persistent-parameter writes, periodic TX, monitor, raw TX."""
    with pytest.raises(UnsafeCommand):
        check_command(cmd)


def test_T_S05_uds_read_gate():
    """T-S05 | SC-7 | D-011, G-004 | UDS 0x19 {01,02,0A} and 0x22 <DID> only with uds_read=True."""
    assert check_command("19 02 FF", uds_read=True) == "1902FF"
    assert check_command("19 0A", uds_read=True) == "190A"
    assert check_command("22 F1 90", uds_read=True) == "22F190"
    for bad in ("19 04 01 33 01", "19", "22", "22 F1", "2E F1 90 00", "14 FF FF FF"):
        with pytest.raises(UnsafeCommand):
            check_command(bad, uds_read=True)


def test_T_S06_transport_refuses_before_writing():
    """T-S06 | SC-6 | D-012 | the transport calls check_command before any byte reaches the port."""
    port = FakeElm()
    t = ElmTransport(port)
    t.open()
    before = list(port.writes)
    for bad in ("04", "14 FF FF FF", "01 0C\rATZ"):
        with pytest.raises(UnsafeCommand):
            t.send(bad)
    assert port.writes == before


def test_T_S07_every_written_frame_is_canonical(fake_elm):
    """T-S07 | SC-6 | D-012 | writes are exactly canonical command + CR (no smuggled bytes)."""
    t = ElmTransport(fake_elm)
    t.open()
    t.send("01 0c")
    t.send("at rv")
    assert fake_elm.writes, "nothing written"
    for w in fake_elm.writes:
        assert re.fullmatch(rb"[0-9A-Z@]{2,32}\r", w), w
