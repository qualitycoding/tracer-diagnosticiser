"""Command-line interface (D-017). Subcommands: probe, dtc, live, info, report. No write/clear commands."""
from __future__ import annotations

import argparse
import datetime
import os
import sys
import time

from .errors import AdapterNoResponse, AdapterNotFound, NoData, ProtocolError, UnsupportedPid
from .pids import PID_TABLE
from .vehicle import redact_vin as _redact_vin_str

EXIT_OK, EXIT_USAGE, EXIT_ADAPTER, EXIT_VEHICLE, EXIT_INTERRUPTED = 0, 2, 3, 4, 130

_DEFAULT_PIDS = "0C,05,0D,11"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tracer-diag",
        description="Read-only diagnostics for a 2022 Yamaha Tracer 9 GT (UK, Euro 5).",
    )
    parser.add_argument("--port", help="serial port, e.g. COM7 or /dev/ttyUSB0 (else TRACER_DIAG_PORT)")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--transcript", help="path to append the raw adapter conversation to")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("probe", help="show adapter voltage, detected protocol and answering ECUs")

    dtc_p = sub.add_parser("dtc", help="read stored, pending and permanent trouble codes")
    dtc_p.add_argument("--kind", choices=["stored", "pending", "permanent", "all"], default="all")

    live_p = sub.add_parser("live", help="poll live sensor data and log it to a CSV file")
    live_p.add_argument("--pids", default=_DEFAULT_PIDS, help="comma-separated hex PIDs, e.g. 0C,05")
    live_p.add_argument("--hz", type=float, default=5)
    live_p.add_argument("--duration", type=float, default=10)
    live_p.add_argument("--csv", required=True)

    info_p = sub.add_parser("info", help="show VIN and calibration IDs")
    info_p.add_argument("--show-vin", action="store_true")

    report_p = sub.add_parser("report", help="write a full JSON diagnostic report")
    report_p.add_argument("--out", required=True)
    report_p.add_argument("--show-vin", action="store_true")
    report_p.add_argument("--text", action="store_true", help="also print a human-readable summary")

    return parser


def main(argv: list[str] | None = None, *, transport_factory=None, clock=None, sleep=None) -> int:
    """Entry point. transport_factory(port, baud, timeout) -> unopened ElmTransport-like object.
    clock() -> float seconds (used only by the live loop); sleep(seconds). See D-017.
    """
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code or 0)

    port = args.port or os.environ.get("TRACER_DIAG_PORT")
    if not port:
        print("error: no serial port given; pass --port (e.g. --port COM7) or set TRACER_DIAG_PORT",
              file=sys.stderr)
        return EXIT_USAGE

    clock = clock or time.monotonic
    sleep = sleep or time.sleep

    if transport_factory is None:
        from .transport import ElmTransport, open_serial
        from .transcript import TranscriptLog
        transcript_path = args.transcript

        def transport_factory(p, b, t):
            log = TranscriptLog(transcript_path) if transcript_path else None
            return ElmTransport(open_serial(p, b, t), timeout=t, log=log)

    transport = None
    try:
        transport = transport_factory(port, args.baud, args.timeout)
        transport.open()

        from .session import DiagSession
        session = DiagSession(transport)

        if args.command == "probe":
            _cmd_probe(session)
        elif args.command == "dtc":
            _cmd_dtc(session, args.kind)
        elif args.command == "info":
            _cmd_info(session, args.show_vin)
        elif args.command == "report":
            _cmd_report(session, args.out, args.show_vin, args.text)
        elif args.command == "live":
            _cmd_live(session, args.pids, args.hz, args.duration, args.csv, clock, sleep)

        return EXIT_OK

    except KeyboardInterrupt:
        return EXIT_INTERRUPTED
    except UnsupportedPid as exc:
        print(f"error: unsupported PID {exc}", file=sys.stderr)
        return EXIT_USAGE
    except (AdapterNotFound, AdapterNoResponse) as exc:
        print(f"adapter error: {exc}", file=sys.stderr)
        return EXIT_ADAPTER
    except (NoData, ProtocolError) as exc:
        print(f"vehicle did not answer ({exc}); check the ignition is on and the adapter is seated",
              file=sys.stderr)
        return EXIT_VEHICLE
    finally:
        if transport is not None:
            try:
                transport.close()
            except Exception:
                pass


def _cmd_probe(session) -> None:
    result = session.probe()
    print(f"protocol {result.protocol_number}: {result.protocol_name}")
    print(f"voltage {result.voltage} V")
    print(f"ecus {' '.join(result.ecus)}")


def _cmd_dtc(session, kind: str) -> None:
    kinds = ("stored", "pending", "permanent") if kind == "all" else (kind,)
    for k in kinds:
        codes = [code for group in session.read_dtcs(k).values() for code in group]
        print(f"{k}: " + (", ".join(codes) if codes else "none"))


def _cmd_info(session, show_vin: bool) -> None:
    info = session.read_vehicle_info()
    vin = info.vin
    if vin is not None and not show_vin:
        vin = _redact_vin_str(vin)
    print(f"vin: {vin if vin is not None else 'none'}")
    print(f"calibration_ids: {', '.join(info.calibration_ids) if info.calibration_ids else 'none'}")
    print(f"ecu_name: {info.ecu_name if info.ecu_name else 'none'}")


def _cmd_report(session, out_path: str, show_vin: bool, show_text: bool) -> None:
    from .report import build_report, render_text, write_report

    probe = session.probe()
    monitor = session.read_monitor_status()
    dtcs = {k: session.read_dtcs(k) for k in ("stored", "pending", "permanent")}
    supported = session.read_supported_pids()
    readings = session.read_pids(sorted(set(PID_TABLE) & supported))
    info = session.read_vehicle_info()

    rep = build_report(
        probe=probe, dtcs=dtcs, readings=readings, info=info, monitor=monitor,
        now=datetime.datetime.now(datetime.timezone.utc), redact_vin=not show_vin,
    )
    write_report(rep, out_path)
    if show_text:
        print(render_text(rep), end="")


def _cmd_live(session, pids_arg: str, hz: float, duration: float, csv_path: str, clock, sleep) -> None:
    try:
        pids = [int(tok, 16) for tok in pids_arg.split(",")]
    except ValueError:
        raise UnsupportedPid(f"could not parse --pids {pids_arg!r} as comma-separated hex") from None

    for pid in pids:
        if pid not in PID_TABLE:
            raise UnsupportedPid(f"0x{pid:02X}")

    names = [PID_TABLE[pid][0] for pid in pids]
    interval = 1.0 / hz

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        f.write("t," + ",".join(names) + "\n")
        f.flush()

        start = clock()
        while True:
            now = clock()
            if now - start >= duration:
                break
            readings = session.read_pids(pids)
            row = [str(now)]
            for pid in pids:
                value = ""
                for header in sorted(readings):
                    match = next((r for r in readings[header] if r.pid == pid), None)
                    if match is not None:
                        value = str(match.value)
                        break
                row.append(value)
            f.write(",".join(row) + "\n")
            f.flush()
            sleep(interval)
