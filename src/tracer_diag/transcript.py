"""Append-only raw adapter transcript (D-015)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, TextIO


class TranscriptLog:
    def __init__(self, path: str, clock: Callable[[], datetime] | None = None) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._fh: TextIO | None = open(path, "a", encoding="utf-8")

    def _write(self, direction: str, text: str) -> None:
        if self._fh is None:
            return
        self._fh.write(f"{self._clock().isoformat()} {direction} {text}\n")
        self._fh.flush()

    def tx(self, text: str) -> None:
        self._write("TX", text)

    def rx(self, text: str) -> None:
        self._write("RX", text)

    def close(self) -> None:
        if self._fh is not None:
            self._fh.close()
            self._fh = None
