"""Parse ELM327/STN text responses (headers on, spaces on) into per-ECU payloads (D-012)."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .errors import NoData, ProtocolError

_HEX2 = re.compile(r"^[0-9A-F]{2}$")
_HEX3 = re.compile(r"^[0-9A-F]{3}$")
_ERROR_SUBSTRINGS = (
    "UNABLE TO CONNECT", "CAN ERROR", "BUS ERROR", "ERROR",
    "STOPPED", "BUFFER FULL", "FB ERROR", "DATA ERROR",
)


@dataclass(frozen=True)
class EcuReply:
    header: str   # '7E8' (11-bit) or '18DAF110' (29-bit), upper-case, no spaces
    data: bytes   # reassembled ISO-TP payload (service byte first), PCI bytes removed


class _Assembly:
    __slots__ = ("total_len", "buf", "next_seq")

    def __init__(self, total_len: int) -> None:
        self.total_len = total_len
        self.buf = bytearray()
        self.next_seq = 1  # first consecutive frame is sequence 1


def parse_response(lines: list[str]) -> list[EcuReply]:
    """Convert adapter output lines (prompt and echo already stripped) into EcuReply objects,
    ordered by first appearance of each header. See D-012 for error mapping."""
    replies: list[EcuReply] = []
    assemblies: dict[str, _Assembly] = {}
    saw_no_data = False

    for raw in lines:
        line = raw.strip()
        if not line or line == "SEARCHING...":
            continue
        if line == "NO DATA":
            saw_no_data = True
            continue
        if line == "?" or any(sub in line for sub in _ERROR_SUBSTRINGS):
            raise ProtocolError(line)

        tokens = line.split()
        if tokens and _HEX3.match(tokens[0]):
            header = tokens[0]
            rest = tokens[1:]
        elif len(tokens) >= 5 and all(_HEX2.match(t) for t in tokens[:4]):
            header = "".join(tokens[:4])
            rest = tokens[4:]
        else:
            raise ProtocolError(line)

        if not rest or not all(_HEX2.match(t) for t in rest):
            raise ProtocolError(line)

        payload = bytes(int(t, 16) for t in rest)
        pci_nibble = payload[0] >> 4

        if pci_nibble == 0x0:
            length = payload[0] & 0x0F
            if len(payload) - 1 < length:
                raise ProtocolError(line)
            replies.append(EcuReply(header, payload[1:1 + length]))

        elif pci_nibble == 0x1:
            length = ((payload[0] & 0x0F) << 8) | payload[1]
            assembly = _Assembly(length)
            assembly.buf.extend(payload[2:])
            assemblies[header] = assembly

        elif pci_nibble == 0x2:
            assembly = assemblies.get(header)
            if assembly is None:
                raise ProtocolError(line)
            seq = payload[0] & 0x0F
            if seq != assembly.next_seq:
                raise ProtocolError(line)
            assembly.buf.extend(payload[1:])
            assembly.next_seq = (assembly.next_seq + 1) % 16
            if len(assembly.buf) >= assembly.total_len:
                replies.append(EcuReply(header, bytes(assembly.buf[:assembly.total_len])))
                del assemblies[header]

        else:
            raise ProtocolError(line)

    if assemblies:
        raise ProtocolError("incomplete multi-frame response")

    if not replies:
        if saw_no_data:
            raise NoData()
        raise ProtocolError("no data in response")

    return replies
