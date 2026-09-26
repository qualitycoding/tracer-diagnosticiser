"""Mode 09 vehicle information (D-013)."""
from __future__ import annotations

import re

from .errors import ProtocolError

_VIN_RE = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")


def decode_vin(payload: bytes) -> str:
    """payload = full reassembled mode-09 PID-02 response: 49 02 01 + 17 ASCII bytes."""
    if payload[:2] != b"\x49\x02":
        raise ProtocolError(payload)
    vin = payload[3:].strip(b"\x00").decode("ascii", errors="strict")
    if not _VIN_RE.match(vin):
        raise ProtocolError(payload)
    return vin


def redact_vin(vin: str) -> str:
    """Keep the 3-char WMI and the last 6 chars; replace the middle 8 with '*'."""
    if len(vin) != 17:
        raise ValueError(vin)
    return vin[:3] + "*" * 8 + vin[-6:]
