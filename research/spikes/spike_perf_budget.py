"""Spike S6 (D-019): measure median wall time of the T-P01/T-P02 workloads against the discarded
reference implementation (see spike_refimpl.out.txt). Budgets in tests = >= 5x these medians.
Run: PYTHONPATH=<refimpl dir> python research/spikes/spike_perf_budget.py"""
import statistics, tempfile, time, os, sys
sys.path.insert(0, os.getcwd())
from tracer_diag.elm_parse import parse_response
from tracer_diag import cli
from tracer_diag.transport import ElmTransport
from tests.fixtures.fake_elm import FakeElm, FakeClock
a, b = [], []
for _ in range(7):
    t = time.perf_counter(); parse_response(["7E8 04 41 0C 1A F8 "] * 10_000); a.append(time.perf_counter() - t)
    with tempfile.TemporaryDirectory() as d:
        t = time.perf_counter()
        cli.main(["--port", "X", "live", "--pids", "0C,05,0D,11", "--hz", "1000", "--duration", "0.2", "--csv", d + "/l.csv"],
                 transport_factory=lambda p, bd, to: ElmTransport(FakeElm()), clock=FakeClock(step=0.001), sleep=lambda s: None)
        b.append(time.perf_counter() - t)
print(f"T-P01 median {statistics.median(a):.4f}s (budget 1.0s, headroom {1.0/statistics.median(a):.0f}x)")
print(f"T-P02 median {statistics.median(b):.4f}s (budget 2.0s, headroom {2.0/statistics.median(b):.0f}x)")
