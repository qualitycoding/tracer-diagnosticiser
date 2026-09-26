# FROZEN — DO NOT MODIFY (tests/FROZEN_MANIFEST.sha256)
"""Unit tests for tracer_diag.elm_parse (D-012). Line formats from spike S5 (C-020)."""
import pytest
from tracer_diag.elm_parse import parse_response, EcuReply
from tracer_diag.errors import ProtocolError, NoData


def test_T_U13_single_frame_with_and_without_padding():
    """T-U13 | SC-1 | C-020 | PCI length trims CAN padding; trailing spaces tolerated."""
    assert parse_response(["7E8 04 41 0C 1A F8 "]) == [EcuReply("7E8", bytes.fromhex("410C1AF8"))]
    assert parse_response(["7E8 04 41 0C 1A F8 00 00 00"]) == [EcuReply("7E8", bytes.fromhex("410C1AF8"))]


def test_T_U14_multiple_ecus_in_order():
    """T-U14 | SC-1 | D-012 | one EcuReply per complete message, in completion order."""
    out = parse_response(["SEARCHING...", "7E8 06 41 00 98 3B 80 13 ", "7E9 06 41 00 80 00 00 01 "])
    assert [r.header for r in out] == ["7E8", "7E9"]
    assert out[1].data == bytes.fromhex("410080000001")


def test_T_U15_multi_frame_reassembly_vin():
    """T-U15 | SC-4 | C-020 | ISO-TP first frame (0x1L LL) + consecutive frames (0x2N)."""
    lines = ["7E8 10 14 49 02 01 4A 59 41 ", "7E8 21 52 4E 30 30 30 30 4D ", "7E8 22 30 30 31 32 33 34 35 "]
    (r,) = parse_response(lines)
    assert r.header == "7E8" and r.data == bytes.fromhex("490201") + b"JYARN0000M0012345"


def test_T_U16_multi_frame_trims_to_declared_length():
    """T-U16 | SC-4 | D-012 | last CF padding beyond FF length is discarded."""
    lines = ["7E8 10 13 49 04 01 42 37 4E ", "7E8 21 38 35 39 31 41 30 30 ", "7E8 22 00 00 00 00 00 00 00 "]
    (r,) = parse_response(lines)
    assert len(r.data) == 0x13 and r.data.startswith(bytes.fromhex("490401"))


def test_T_U17_29bit_headers():
    """T-U17 | SC-1 | D-012 | 29-bit header = first four byte tokens."""
    assert parse_response(["18 DA F1 10 03 41 05 7B "]) == [EcuReply("18DAF110", bytes.fromhex("41057B"))]


def test_T_U18_no_data():
    """T-U18 | SC-5 | D-012 | 'NO DATA' with no data lines -> NoData."""
    with pytest.raises(NoData):
        parse_response(["NO DATA"])
    with pytest.raises(NoData):
        parse_response(["SEARCHING...", "NO DATA"])


@pytest.mark.parametrize("line", ["UNABLE TO CONNECT", "CAN ERROR", "BUS INIT: ...ERROR", "?",
                                  "STOPPED", "BUFFER FULL", "<RX ERROR", "7E8 04 41 0C 1A", "7E8 04 41 0C ZZ F8",
                                  "7E8 21 52 4E 30 30 30 30 4D"])
def test_T_U19_errors_and_malformed(line):
    """T-U19 | SC-5 | D-012 | adapter error strings, short frames, non-hex, orphan CF -> ProtocolError."""
    with pytest.raises(ProtocolError):
        parse_response([line])


def test_T_U20_incomplete_or_out_of_sequence_multiframe():
    """T-U20 | SC-4 | D-012."""
    with pytest.raises(ProtocolError):
        parse_response(["7E8 10 14 49 02 01 4A 59 41 ", "7E8 21 52 4E 30 30 30 30 4D "])
    with pytest.raises(ProtocolError):
        parse_response(["7E8 10 14 49 02 01 4A 59 41 ", "7E8 22 52 4E 30 30 30 30 4D ", "7E8 21 30 30 31 32 33 34 35 "])
