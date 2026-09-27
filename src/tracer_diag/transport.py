"""ELM327/STN serial transport (D-012). Every command passes safety.check_command first."""
from __future__ import annotations

from typing import Protocol

from .errors import AdapterNoResponse, AdapterNotFound, ProtocolError
from .safety import check_command


class SerialLike(Protocol):
    timeout: float | None
    def write(self, data: bytes) -> int: ...
    def read(self, size: int = 1) -> bytes: ...
    def reset_input_buffer(self) -> None: ...
    def close(self) -> None: ...


INIT_SEQUENCE: tuple[str, ...] = ("ATZ", "ATE0", "ATL0", "ATS1", "ATH1", "ATSP0")


def open_serial(path: str, baud: int = 115200, timeout: float = 5.0) -> SerialLike:
    """Open a pyserial port; raise AdapterNotFound if it cannot be opened."""
    import serial

    try:
        return serial.Serial(path, baud, timeout=timeout)
    except (serial.SerialException, OSError, ValueError) as exc:
        raise AdapterNotFound(str(exc)) from exc


class ElmTransport:
    def __init__(self, port: SerialLike, *, timeout: float = 5.0, log=None, uds_read: bool = False) -> None:
        self._port = port
        self._timeout = timeout
        self._log = log
        self._uds_read = uds_read

    def open(self) -> None:
        """Send INIT_SEQUENCE; raise AdapterNoResponse if ATZ gets no prompt."""
        self._port.reset_input_buffer()
        for cmd in INIT_SEQUENCE:
            lines = self.send(cmd)
            if cmd == "ATZ":
                if not any("ELM327" in line for line in lines):
                    raise ProtocolError(f"{cmd}: {lines}")
            else:
                if not any("OK" in line for line in lines):
                    raise ProtocolError(f"{cmd}: {lines}")

    def send(self, cmd: str) -> list[str]:
        """check_command -> write cmd+'\\r' -> read to '>' -> return non-empty lines minus echo."""
        canonical = check_command(cmd, uds_read=self._uds_read)
        if self._log is not None:
            self._log.tx(canonical)

        self._port.write((canonical + "\r").encode("ascii"))

        buf = b""
        while not buf.endswith(b">"):
            chunk = self._port.read(64)
            if not chunk:
                raise AdapterNoResponse(canonical)
            buf += chunk

        text = buf[:-1].decode("ascii", errors="replace")
        text = text.replace("\n", "\r")
        raw_lines = [line.strip() for line in text.split("\r")]
        lines = [line for line in raw_lines if line]

        if lines and "".join(lines[0].split()).upper() == canonical:
            lines = lines[1:]

        if self._log is not None:
            for line in lines:
                self._log.rx(line)

        return lines

    def close(self) -> None:
        self._port.close()
