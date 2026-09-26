"""Diagnostic trouble code decoding (D-013)."""
from __future__ import annotations

from .errors import ProtocolError

DTC_SERVICES = {"stored": 0x03, "pending": 0x07, "permanent": 0x0A}

_LETTER = "PCBU"


def decode_dtc(two: bytes) -> str:
    """Decode a 2-byte DTC into 'P0133' form (SAE J2012 first-two-bits letter rule)."""
    if len(two) != 2:
        raise ProtocolError(two)
    b0, b1 = two[0], two[1]
    letter = _LETTER[b0 >> 6]
    first_digit = (b0 >> 4) & 0x3
    return f"{letter}{first_digit}{b0 & 0xF:X}{b1 >> 4:X}{b1 & 0xF:X}"


def parse_dtc_list(payload: bytes, service: int) -> list[str]:
    """Decode a CAN mode 03/07/0A response payload (0x43/0x47/0x4A, count byte, pairs).
    Drops 0x0000 padding. Raises ProtocolError on wrong response byte or odd length."""
    if len(payload) < 2 or payload[0] != service + 0x40:
        raise ProtocolError(payload)
    rest = payload[2:]
    if len(rest) % 2 != 0:
        raise ProtocolError(payload)
    codes = []
    for i in range(0, len(rest), 2):
        pair = rest[i:i + 2]
        if pair == b"\x00\x00":
            continue
        codes.append(decode_dtc(pair))
    return codes
