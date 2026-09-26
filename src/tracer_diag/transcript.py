"""Append-only raw adapter transcript (D-015)."""
from __future__ import annotations
from typing import Callable
from datetime import datetime


class TranscriptLog:
    def __init__(self, path: str, clock: Callable[[], datetime] | None = None) -> None:
        raise NotImplementedError("S-005")

    def tx(self, text: str) -> None:
        raise NotImplementedError("S-005")

    def rx(self, text: str) -> None:
        raise NotImplementedError("S-005")

    def close(self) -> None:
        raise NotImplementedError("S-005")
