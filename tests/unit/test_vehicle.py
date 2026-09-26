# FROZEN — DO NOT MODIFY (tests/FROZEN_MANIFEST.sha256)
"""Unit tests for tracer_diag.vehicle (D-013)."""
import pytest
from tracer_diag.vehicle import decode_vin, redact_vin
from tracer_diag.errors import ProtocolError


def test_T_U21_decode_vin():
    """T-U21 | SC-4 | D-013 | 49 02 01 + 17 ASCII; leading/trailing 0x00 stripped."""
    assert decode_vin(bytes.fromhex("490201") + b"JYARN0000M0012345") == "JYARN0000M0012345"
    assert decode_vin(bytes.fromhex("49020100") + b"JYARN0000M0012345" + b"\x00") == "JYARN0000M0012345"


@pytest.mark.parametrize("payload", [
    bytes.fromhex("490201") + b"JYARN0000M001234",       # 16 chars
    bytes.fromhex("490201") + b"JYARN0000M001234O",      # 'O' not allowed in a VIN
    bytes.fromhex("410201") + b"JYARN0000M0012345",      # wrong service byte
])
def test_T_U22_decode_vin_rejects_invalid(payload):
    """T-U22 | SC-4 | D-013 | ISO 3779 charset (no I, O, Q), 17 chars, 0x49 0x02 prefix."""
    with pytest.raises(ProtocolError):
        decode_vin(payload)


def test_T_U23_redact_vin():
    """T-U23 | SC-6 | D-013 | WMI + 8 stars + last 6 (privacy default for shared reports)."""
    assert redact_vin("JYARN0000M0012345") == "JYA********012345"
    with pytest.raises(ValueError):
        redact_vin("SHORT")
