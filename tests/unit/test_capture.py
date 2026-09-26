# FROZEN — DO NOT MODIFY (tests/FROZEN_MANIFEST.sha256)
"""Unit tests for passive capture (D-018) using python-can's virtual interface (C-016)."""
import can
from tracer_diag import capture
from tests.fixtures.fake_elm import FakeClock


def test_T_U27_capture_writes_candump_lines(tmp_path):
    """T-U27 | SC-7 | D-018 | candump -L format '(ts) can0 ID#DATA'; one line per received frame."""
    rx = capture.open_listen_only("tdiag", interface="virtual")
    tx = can.Bus(interface="virtual", channel="tdiag")
    for data in (b"\x03\x41\x0c\x1a", b"\x03\x41\x05\x7b", b"\x01\x02"):
        tx.send(can.Message(arbitration_id=0x7E8, data=data, is_extended_id=False, timestamp=1790000000.5))
    out = tmp_path / "cap.log"
    n = capture.capture(rx, 1.0, str(out), clock=FakeClock(start=0.0, step=0.25))
    lines = out.read_text(encoding="utf-8").splitlines()
    assert n == 3 and len(lines) == 3
    assert lines[0].endswith(" can0 7E8#03410C1A") and lines[0].startswith("(")
    assert capture.summarize(str(out)) == {"7E8": 3}
    tx.shutdown(); rx.shutdown()
