"""Mode 09 vehicle information (D-013)."""
from __future__ import annotations


def decode_vin(payload: bytes) -> str:
    """payload = full reassembled mode-09 PID-02 response: 49 02 01 + 17 ASCII bytes."""
    raise NotImplementedError("S-004")


def redact_vin(vin: str) -> str:
    """Keep the 3-char WMI and the last 6 chars; replace the middle 8 with '*'."""
    raise NotImplementedError("S-004")
