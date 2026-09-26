"""Parse ELM327/STN text responses (headers on, spaces on) into per-ECU payloads (D-012)."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class EcuReply:
    header: str   # '7E8' (11-bit) or '18DAF110' (29-bit), upper-case, no spaces
    data: bytes   # reassembled ISO-TP payload (service byte first), PCI bytes removed


def parse_response(lines: list[str]) -> list[EcuReply]:
    """Convert adapter output lines (prompt and echo already stripped) into EcuReply objects,
    ordered by first appearance of each header. See D-012 for error mapping."""
    raise NotImplementedError("S-003")
