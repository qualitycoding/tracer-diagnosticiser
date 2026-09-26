"""Diagnostic trouble code decoding (D-013)."""
from __future__ import annotations

DTC_SERVICES = {"stored": 0x03, "pending": 0x07, "permanent": 0x0A}


def decode_dtc(two: bytes) -> str:
    """Decode a 2-byte DTC into 'P0133' form (SAE J2012 first-two-bits letter rule)."""
    raise NotImplementedError("S-004")


def parse_dtc_list(payload: bytes, service: int) -> list[str]:
    """Decode a CAN mode 03/07/0A response payload (0x43/0x47/0x4A, count byte, pairs).
    Drops 0x0000 padding. Raises ProtocolError on wrong response byte or odd length."""
    raise NotImplementedError("S-004")
