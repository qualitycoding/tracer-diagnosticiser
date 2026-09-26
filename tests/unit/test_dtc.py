# FROZEN — DO NOT MODIFY (tests/FROZEN_MANIFEST.sha256)
"""Unit tests for tracer_diag.dtc (D-013). Expected values from spike S2 oracle (C-014)."""
import pytest
from tracer_diag.dtc import decode_dtc, parse_dtc_list
from tracer_diag.errors import ProtocolError


@pytest.mark.parametrize("raw,code", [
    ("0133", "P0133"), ("0420", "P0420"), ("4123", "C0123"),
    ("8001", "B0001"), ("C155", "U0155"), ("1234", "P1234"), ("3FFF", "P3FFF"),
])
def test_T_U01_decode_dtc_letter_and_digits(raw, code):
    """T-U01 | SC-2 | C-014 | first two bits select P/C/B/U; remaining 14 bits as 4 hex digits."""
    assert decode_dtc(bytes.fromhex(raw)) == code


@pytest.mark.parametrize("raw", ["", "01", "013300"])
def test_T_U02_decode_dtc_rejects_wrong_length(raw):
    """T-U02 | SC-2 | D-013 | a DTC is exactly two bytes."""
    with pytest.raises(ProtocolError):
        decode_dtc(bytes.fromhex(raw))


def test_T_U03_parse_dtc_list_stored_drops_padding():
    """T-U03 | SC-2 | C-014 | 0x43, count, pairs; 0x0000 padding is not a DTC."""
    assert parse_dtc_list(bytes.fromhex("430301330420" + "0000"), 0x03) == ["P0133", "P0420"]


def test_T_U04_parse_dtc_list_empty_and_other_services():
    """T-U04 | SC-2 | D-013 | services 0x07 and 0x0A use response bytes 0x47 / 0x4A."""
    assert parse_dtc_list(bytes.fromhex("4700"), 0x07) == []
    assert parse_dtc_list(bytes.fromhex("4A01C155"), 0x0A) == ["U0155"]


@pytest.mark.parametrize("payload,service", [("4700", 0x03), ("43010133FF", 0x03), ("", 0x03)])
def test_T_U05_parse_dtc_list_rejects_malformed(payload, service):
    """T-U05 | SC-2 | D-013 | wrong response byte, odd pair bytes, or empty payload -> ProtocolError."""
    with pytest.raises(ProtocolError):
        parse_dtc_list(bytes.fromhex(payload), service)
