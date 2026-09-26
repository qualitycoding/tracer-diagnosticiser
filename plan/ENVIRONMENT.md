# Environment (pinned, verified in the planning sandbox 2026-09-26)

| Item | Version |
|---|---|
| Python | 3.12.3 (any 3.12.x; `requires-python >=3.12,<3.13`) |
| pip | 26.2.1 (planning sandbox; any recent pip supports `--require-hashes`) |
| pyserial | 3.5 (runtime) |
| setuptools | 84.0.0 (build backend; 80.9.0 was rejected: PYSEC-2026-3447, fixed in 83.0.0) |
| python-can | 4.6.1 (optional `capture` extra; dev) |
| pytest | 9.1.1 (dev) |
| pip-audit | 2.10.1 (dev) |
| pip-tools | 7.6.1 (only to regenerate lockfiles) |

Lockfiles: `requirements.txt` (runtime, hashed) and `requirements-dev.txt` (dev, hashed), generated with
`pip-compile --strip-extras --generate-hashes --allow-unsafe -o <out> <in>` from `requirements.in` / `requirements-dev.in`.

## Implementer setup (Linux; verified)
```bash
python3.12 -m venv .venv && . .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.txt
python -m pip install --no-deps --no-build-isolation -e .
sha256sum -c tests/FROZEN_MANIFEST.sha256
python -m pytest -q            # at generation time: 174 failed (red baseline), 0 errors
```
Verified output: install succeeded; `pip-audit` on both lockfiles: "No known vulnerabilities found"; red run `174 failed` (research/spikes/red_verification_junit.xml).

## Human runtime setup (Windows 10/11, PowerShell) — used at G-003
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --require-hashes -r requirements.txt
python -m pip install --no-deps --no-build-isolation .
tracer-diag --help
```
Not executed in the planning sandbox (no Windows); covered by G-003 (R-021).

## Bluetooth (MX+) on Windows
Press the MX+ pair button, then Settings > Bluetooth & devices > Add device > Bluetooth > OBDLink MX+ (enter PIN 0000 if asked; C-012). Find the outgoing COM port in Settings > Bluetooth & devices > Devices > More Bluetooth settings > COM Ports, and pass it as `--port COMn` (standard Windows dialog; its exact menu path was not verified in this run — if it differs, use Device Manager > Ports (COM & LPT)).
