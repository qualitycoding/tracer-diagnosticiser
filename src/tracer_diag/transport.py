"""ELM327/STN serial transport (D-012). Every command passes safety.check_command first."""
from __future__ import annotations
from typing import Protocol


class SerialLike(Protocol):
    timeout: float | None
    def write(self, data: bytes) -> int: ...
    def read(self, size: int = 1) -> bytes: ...
    def reset_input_buffer(self) -> None: ...
    def close(self) -> None: ...


INIT_SEQUENCE: tuple[str, ...] = ("ATZ", "ATE0", "ATL0", "ATS1", "ATH1", "ATSP0")


def open_serial(path: str, baud: int = 115200, timeout: float = 5.0) -> SerialLike:
    """Open a pyserial port; raise AdapterNotFound if it cannot be opened."""
    raise NotImplementedError("S-005")


class ElmTransport:
    def __init__(self, port: SerialLike, *, timeout: float = 5.0, log=None, uds_read: bool = False) -> None:
        raise NotImplementedError("S-005")

    def open(self) -> None:
        """Send INIT_SEQUENCE; raise AdapterNoResponse if ATZ gets no prompt."""
        raise NotImplementedError("S-005")

    def send(self, cmd: str) -> list[str]:
        """check_command -> write cmd+'\\r' -> read to '>' -> return non-empty lines minus echo."""
        raise NotImplementedError("S-005")

    def close(self) -> None:
        raise NotImplementedError("S-005")
