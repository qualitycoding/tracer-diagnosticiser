# FROZEN — DO NOT MODIFY (tests/FROZEN_MANIFEST.sha256)
"""Deterministic in-memory ELM327/STN double implementing transport.SerialLike.

Response formats mirror ELM327-emulator 4.0.0 output captured in
research/spikes/spike_emu_raw.out.txt (C-020): '\\r'-separated lines, trailing space
after data lines, final '\\r\\r>' prompt; echo on until ATE0.
Scripted payloads are in TRACER_SCRIPT (fictitious VIN; C-015 oracle values).
"""
from __future__ import annotations


TRACER_SCRIPT: dict[str, list[str]] = {
    "ATZ": ["", "", "ELM327 v1.4b"],
    "ATE0": ["OK"], "ATL0": ["OK"], "ATS1": ["OK"], "ATH1": ["OK"], "ATSP0": ["OK"],
    "ATRV": ["12.6V"],
    "ATDPN": ["A6"],
    "ATDP": ["AUTO, ISO 15765-4 (CAN 11/500) "],
    "0100": ["SEARCHING...", "7E8 06 41 00 98 3B 80 13 "],
    "0120": ["7E8 06 41 20 00 00 00 01 "],
    "0140": ["7E8 06 41 40 40 00 00 00 "],
    "0101": ["7E8 06 41 01 82 07 65 04 "],
    "03": ["7E8 06 43 02 01 33 04 20 "],
    "07": ["7E8 02 47 00 "],
    "0A": ["NO DATA"],
    "010C": ["7E8 04 41 0C 1A F8 "],
    "0105": ["7E8 03 41 05 7B "],
    "010D": ["7E8 03 41 0D 00 "],
    "0111": ["7E8 03 41 11 80 "],
    "0104": ["7E8 03 41 04 FF "],
    "011C": ["7E8 03 41 1C 03 "],
    "010F": ["7E8 03 41 0F 3C "],
    "010B": ["7E8 03 41 0B 65 "],
    "0142": ["7E8 04 41 42 32 00 "],
    "0902": ["7E8 10 14 49 02 01 4A 59 41 ",
             "7E8 21 52 4E 30 30 30 30 4D ",
             "7E8 22 30 30 31 32 33 34 35 "],
    "0904": ["7E8 10 13 49 04 01 42 37 4E ",
             "7E8 21 38 35 39 31 41 30 30 ",
             "7E8 22 00 00 00 00 00 00 00 "],
    "090A": ["NO DATA"],
}
FAKE_VIN = "JYARN0000M0012345"


class FakeElm:
    """SerialLike double. `script` maps canonical command -> response lines.
    Unknown commands answer '?'. `silent=True` never answers (read returns b'').
    `interrupt_on` raises KeyboardInterrupt when that canonical command is written.
    `overrides` replaces individual script entries."""

    def __init__(self, script=None, *, silent=False, interrupt_on=None, overrides=None):
        self.script = dict(TRACER_SCRIPT if script is None else script)
        if overrides:
            self.script.update(overrides)
        self.silent = silent
        self.interrupt_on = interrupt_on
        self.timeout = 1.0
        self.echo = True
        self.writes: list[bytes] = []
        self.commands: list[str] = []
        self.closed = False
        self._buf = bytearray()

    def write(self, data: bytes) -> int:
        self.writes.append(bytes(data))
        text = data.decode("ascii", "replace")
        for raw in text.split("\r"):
            if not raw:
                continue
            cmd = "".join(raw.split()).upper()
            self.commands.append(cmd)
            if self.interrupt_on is not None and cmd == self.interrupt_on:
                raise KeyboardInterrupt
            if self.silent:
                continue
            lines = self.script.get(cmd, ["?"])
            out = (raw + "\r") if self.echo else ""
            if cmd == "ATE0":
                self.echo = False
            out += "\r".join(lines) + "\r\r>"
            self._buf.extend(out.encode("ascii"))
        return len(data)

    def read(self, size: int = 1) -> bytes:
        chunk = bytes(self._buf[:size])
        del self._buf[:size]
        return chunk

    def reset_input_buffer(self) -> None:
        self._buf.clear()

    def close(self) -> None:
        self.closed = True


class FakeClock:
    """Deterministic clock: each call advances by `step` seconds."""

    def __init__(self, start: float = 1_790_000_000.0, step: float = 0.1):
        self.t = start - step
        self.step = step

    def __call__(self) -> float:
        self.t += self.step
        return self.t
