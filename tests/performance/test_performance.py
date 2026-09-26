# FROZEN — DO NOT MODIFY (tests/FROZEN_MANIFEST.sha256)
"""Performance tests (D-019). Budget: software must out-run the fastest adapter in scope
(OBDLink EX ~200 PIDs/s, MX+ ~100 PIDs/s; C-011) with >= 2x headroom on a laptop-class CPU.
Variance tolerance: wall-clock budgets are 5x the median measured in spike S6 on the planning sandbox."""
import time
from tracer_diag.elm_parse import parse_response
from tracer_diag import cli
from tracer_diag.transport import ElmTransport
from tests.fixtures.fake_elm import FakeElm, FakeClock


def test_T_P01_parse_throughput():
    """T-P01 | SC-3 | D-019 | 10,000 single-frame lines parse in < 1.0 s."""
    lines = ["7E8 04 41 0C 1A F8 "] * 10_000
    t0 = time.perf_counter()
    out = parse_response(lines)
    assert time.perf_counter() - t0 < 1.0 and len(out) == 10_000


def test_T_P02_live_loop_overhead(tmp_path):
    """T-P02 | SC-3 | D-019 | 4 PIDs x 199 iterations against a zero-latency adapter in < 2.0 s
    (>= 400 PIDs/s software throughput = 2x the fastest adapter)."""
    out = tmp_path / "live.csv"
    t0 = time.perf_counter()
    rc = cli.main(["--port", "COM7", "live", "--pids", "0C,05,0D,11", "--hz", "1000", "--duration", "0.2",
                   "--csv", str(out)], transport_factory=lambda p, b, t: ElmTransport(FakeElm()),
                  clock=FakeClock(step=0.001), sleep=lambda s: None)
    assert rc == 0 and time.perf_counter() - t0 < 2.0
    assert len(out.read_text(encoding="utf-8").splitlines()) >= 150
