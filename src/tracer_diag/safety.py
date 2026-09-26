"""Read-only command allowlist (D-011). The single chokepoint for every byte sent to the adapter."""
from __future__ import annotations

import re

from .errors import UnsafeCommand

# Data declarations (frozen by D-011). Behaviour lives in check_command().
ALLOWED_OBD_SERVICES: frozenset[int] = frozenset({0x01, 0x02, 0x03, 0x06, 0x07, 0x09, 0x0A})
ALLOWED_UDS_READ: dict[int, frozenset[int] | None] = {0x19: frozenset({0x01, 0x02, 0x0A}), 0x22: None}
MAX_COMMAND_LEN = 32

_AT_ST_EXACT = frozenset({
    "ATZ", "ATWS", "ATI", "AT@1", "ATE0", "ATL0", "ATS1", "ATH1", "ATH0",
    "ATRV", "ATDP", "ATDPN", "ATCAF1", "ATAT1", "ATAT2", "STI", "STDI",
})
_AT_ST_PATTERNS = (
    re.compile(r"^ATSP[0-9]$"),
    re.compile(r"^ATST[0-9A-F]{2}$"),
    re.compile(r"^ATSH(?:[0-9A-F]{3}|[0-9A-F]{6})$"),
)
_DISALLOWED_CHARS = frozenset({">"})


def check_command(cmd: str, *, uds_read: bool = False) -> str:
    """Return the canonical form of `cmd` if it is allowed, else raise UnsafeCommand.

    Canonical form: upper-case, all whitespace removed (e.g. '01 0c' -> '010C', 'at rv' -> 'ATRV').
    Rules are specified in plan/DECISIONS.md D-011.
    """
    for ch in cmd:
        if ch in _DISALLOWED_CHARS:
            raise UnsafeCommand(cmd)
        code = ord(ch)
        if code < 0x20 and ch not in (" ", "\t"):
            raise UnsafeCommand(cmd)
        if code == 0x7F:
            raise UnsafeCommand(cmd)

    canonical = "".join(cmd.split()).upper()

    if not canonical or len(canonical) > MAX_COMMAND_LEN:
        raise UnsafeCommand(cmd)

    if canonical.startswith("AT") or canonical.startswith("ST"):
        if canonical in _AT_ST_EXACT or any(p.match(canonical) for p in _AT_ST_PATTERNS):
            return canonical
        raise UnsafeCommand(cmd)

    if len(canonical) % 2 != 0 or not re.fullmatch(r"[0-9A-F]+", canonical):
        raise UnsafeCommand(cmd)

    data = bytes.fromhex(canonical)
    service = data[0]

    if service in ALLOWED_OBD_SERVICES:
        return canonical

    if uds_read:
        if service == 0x19 and len(data) >= 2 and data[1] in ALLOWED_UDS_READ[0x19]:
            return canonical
        if service == 0x22 and len(data) >= 3:
            return canonical

    raise UnsafeCommand(cmd)
