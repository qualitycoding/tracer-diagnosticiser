"""Read-only command allowlist (D-011). The single chokepoint for every byte sent to the adapter."""
from __future__ import annotations

# Data declarations (frozen by D-011). Behaviour lives in check_command().
ALLOWED_OBD_SERVICES: frozenset[int] = frozenset({0x01, 0x02, 0x03, 0x06, 0x07, 0x09, 0x0A})
ALLOWED_UDS_READ: dict[int, frozenset[int] | None] = {0x19: frozenset({0x01, 0x02, 0x0A}), 0x22: None}
MAX_COMMAND_LEN = 32


def check_command(cmd: str, *, uds_read: bool = False) -> str:
    """Return the canonical form of `cmd` if it is allowed, else raise UnsafeCommand.

    Canonical form: upper-case, all whitespace removed (e.g. '01 0c' -> '010C', 'at rv' -> 'ATRV').
    Rules are specified in plan/DECISIONS.md D-011.
    """
    raise NotImplementedError("S-002")
