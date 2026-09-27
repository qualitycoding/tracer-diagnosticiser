# tracer-diagnosticiser

Read-only on-board diagnostics for a 2022 Yamaha Tracer 9 GT (UK, Euro 5), using the bike's red 6-pin ISO 19689 diagnostic socket, an ISO 19689→OBD-II lead and an OBDLink adapter.

This tool never clears codes and never writes to the bike — see [`plan/DECISIONS.md`](plan/DECISIONS.md) D-011 for the enforced allowlist. Outputs redact the VIN by default.

**Status:** implementation complete (`impl/tracer-diag`), full test suite green (174/174). Hardware not yet purchased or validated on the bike — see [`GATE-G-002a.md`](GATE-G-002a.md). Start with [`HANDOFF.md`](HANDOFF.md) for the full picture; hardware recommendation is in [`plan/HARDWARE.md`](plan/HARDWARE.md).

## Install (Windows 10/11, PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --require-hashes -r requirements.txt
python -m pip install --no-deps --no-build-isolation .
tracer-diag --help
```

## Install (Linux/macOS)

```bash
python3.12 -m venv .venv && . .venv/bin/activate
python -m pip install --require-hashes -r requirements.txt
python -m pip install --no-deps --no-build-isolation .
tracer-diag --help
```

`tracer-diag` needs only `pyserial` at runtime. `python -m tracer_diag` works identically to the `tracer-diag` console script.

## Connecting the adapter

- **USB (e.g. OBDLink EX):** plug in, find the port in Device Manager (Windows: `COMn`; Linux: `/dev/ttyUSBn`).
- **Bluetooth (e.g. OBDLink MX+):** press the adapter's pair button, then Windows Settings → Bluetooth & devices → Add device → Bluetooth → select the adapter (PIN `0000` if asked). Find its outgoing COM port in Settings → Bluetooth & devices → Devices → More Bluetooth settings → COM Ports (or Device Manager → Ports if that path differs on your system).

Every example below assumes the port is `COM7`; substitute your own, or set it once with an environment variable:

```powershell
$env:TRACER_DIAG_PORT = "COM7"
```

## Usage

```
tracer-diag [--port PORT] [--baud BAUD] [--timeout TIMEOUT] [--transcript PATH] <command> ...
```

`--port` may be omitted if `TRACER_DIAG_PORT` is set. `--transcript PATH` records every raw line sent to and received from the adapter (useful for troubleshooting; contains the VIN in full — never commit it).

### `probe` — adapter voltage, detected protocol, answering ECUs

```powershell
tracer-diag --port COM7 probe
```
```
protocol 6: ISO 15765-4 (CAN 11/500)
voltage 12.6 V
ecus 7E8
```

### `dtc` — stored, pending and permanent trouble codes

```powershell
tracer-diag --port COM7 dtc
tracer-diag --port COM7 dtc --kind stored
```
```
stored: P0133, P0420
pending: none
permanent: none
```

### `info` — VIN and calibration IDs

```powershell
tracer-diag --port COM7 info
tracer-diag --port COM7 info --show-vin   # print the full VIN instead of redacted
```
```
vin: JYA********012345
calibration_ids: B7N8591A00
ecu_name: none
```

### `report` — full JSON diagnostic report

```powershell
tracer-diag --port COM7 report --out report.json --text
```
Writes an atomic JSON file (schema version `1`; VIN redacted unless `--show-vin` is given) and, with `--text`, also prints a short human-readable summary. Reports contain the VIN and should stay in a `runs/` directory — never commit them (see `.gitignore`).

### `live` — poll live sensor data to CSV

```powershell
tracer-diag --port COM7 live --pids 0C,05,0D,11 --hz 5 --duration 30 --csv live.csv
```
Polls the given PIDs (comma-separated hex; default `0C,05,0D,11` = RPM, coolant temperature, speed, throttle position) at the given rate for the given duration, writing one CSV row per poll. Press Ctrl-C to stop early; the file written so far is preserved.

## Android

For Android, use a third-party ELM327 app (e.g. Car Scanner ELM OBD2, the OBDLink app) rather than custom software. **These apps can clear codes — do not use that feature**; this project's own guarantee of read-only behaviour applies only to `tracer-diag` itself.

## Development

```bash
python -m pip install --require-hashes -r requirements-dev.txt
python -m pip install --no-deps --no-build-isolation -e .
python -m pytest -q            # 174 passed
pip-audit -r requirements.txt && pip-audit -r requirements-dev.txt
sha256sum -c tests/FROZEN_MANIFEST.sha256
```

Optional stretch feature (passive CAN capture, never transmits): `pip install .[capture]`. See [`plan/DECISIONS.md`](plan/DECISIONS.md) D-018 and gate `G-004`.
