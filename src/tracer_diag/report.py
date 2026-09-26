"""JSON report + text rendering (D-016)."""
from __future__ import annotations
import json  # noqa: F401  (used by write_report; tests patch report.json.dump)
import os  # noqa: F401
import tempfile  # noqa: F401

REPORT_SCHEMA_VERSION = "1"


def build_report(*, probe, dtcs, readings, info, monitor, now, redact_vin: bool = True) -> dict:
    raise NotImplementedError("S-007")


def write_report(report: dict, path: str) -> None:
    """Atomic write: temp file in same directory, then os.replace."""
    raise NotImplementedError("S-007")


def render_text(report: dict) -> str:
    raise NotImplementedError("S-007")
