# Decisions, interfaces and decision rules

## Architecture decisions
- **D-001 Primary interface family:** STN/ELM327-command-set adapters (OBDLink) over a serial port. Genuine STN hardware first, because a clone failing would not tell us whether the bike answers (C-019). Evidence: C-011, C-019.
- **D-002 Physical path:** red ISO 19689 6-pin socket → moulded lead → J1962 16-pin adapter. No splicing into the harness. Evidence: C-001, C-002, C-021.
- **D-003 Lead check before first use:** at G-003 the human measures pin 16 vs pin 4 (or 5) on the lead's 16-pin end with ignition ON; it must read 11.5–14.5 V. Otherwise stop (DR-05e). Evidence: C-004.
- **D-004 Protocol:** automatic detection (`ATSP0`); the parser handles 11-bit and 29-bit CAN headers and ISO-TP multi-frame. K-line responses are handled by the adapter; the tool treats them identically. Evidence: C-005, C-006, C-020.
- **D-005 Own parser, python-OBD only as oracle:** the product does not depend on python-OBD (it exposes a clear-DTC command and cannot be restricted at a single chokepoint). python-OBD was used in spikes to derive expected test values (C-013..C-015).
- **D-006 Language/runtime:** Python 3.12, single runtime dependency `pyserial==3.5`; `python-can==4.6.1` only for the optional `capture` extra (stretch). Runtime install on Windows needs only `requirements.txt` (pyserial + setuptools, hashed).
- **D-007 Ranking tie-break:** weighted scores within 0.10 → prefer the option covering more A-008 platforms.
- **D-008 Privacy:** VIN redacted in every output by default (`--show-vin` opt-in). On-bike outputs go to `runs/` (git-ignored). Transcripts contain the raw VIN bytes and are never committed.
- **D-009 Source layout:** `src/tracer_diag/` package; console script `tracer-diag`; `python -m tracer_diag` also works (S-008 adds `__main__.py`).

## Public interfaces (stubs committed in `src/tracer_diag/`; behaviour below is normative)

### D-010 errors.py (implemented at planning time)
`DiagError` base; subclasses `AdapterNotFound`, `AdapterNoResponse`, `ProtocolError`, `NoData`, `UnsupportedPid`, `UnsafeCommand`. `LowVoltageWarning(UserWarning)`.

### D-011 safety.check_command(cmd: str, *, uds_read: bool = False) -> str
1. If `cmd` contains any character with code < 0x20 other than space and tab, or 0x7F, or `>` → `UnsafeCommand`.
2. Canonical = remove all whitespace (`"".join(cmd.split())`), upper-case.
3. Empty, or longer than `MAX_COMMAND_LEN` (32) → `UnsafeCommand`.
4. If canonical starts with `AT` or `ST`: allowed only if exactly one of `ATZ ATWS ATI AT@1 ATE0 ATL0 ATS1 ATH1 ATH0 ATRV ATDP ATDPN ATCAF1 ATAT1 ATAT2 STI STDI`, or matches `ATSP[0-9]`, `ATST[0-9A-F]{2}`, `ATSH([0-9A-F]{3}|[0-9A-F]{6})`. Everything else (e.g. `ATMA ATPP.. ATSD ATWM ATBD ATSW ATCRA STMA STPX`) → `UnsafeCommand`.
5. Otherwise canonical must be hex digits of even length ≥ 2, else `UnsafeCommand`. Let `b = bytes.fromhex(canonical)`.
6. `b[0]` in `ALLOWED_OBD_SERVICES` {01,02,03,06,07,09,0A} → allowed.
7. Only when `uds_read=True`: `b[0]==0x19` with `len(b)>=2` and `b[1]` in {01,02,0A} → allowed; `b[0]==0x22` with `len(b)>=3` → allowed.
8. Anything else (incl. 04, 05, 08, 10, 11, 14, 27, 28, 2E, 2F, 31, 34–37, 3D, 3E, 85) → `UnsafeCommand`.
Returns the canonical string. Tests: T-S01..T-S05.

### D-012 transport and parser
`INIT_SEQUENCE = ("ATZ","ATE0","ATL0","ATS1","ATH1","ATSP0")`.
- `open_serial(path, baud=115200, timeout=5.0)`: `serial.Serial(path, baud, timeout=timeout)`; any `serial.SerialException`, `OSError` or `ValueError` → `AdapterNotFound`. On Windows `path` is `COMn` (USB VCP or Bluetooth SPP outgoing port, C-012); on Linux `/dev/ttyUSBn` or `/dev/rfcommN`.
- `ElmTransport(port, *, timeout=5.0, log=None, uds_read=False)`.
- `send(cmd)`: `c = check_command(cmd, uds_read=self.uds_read)` **before any write**; `log.tx(c)` if log; `port.write((c + "\r").encode("ascii"))`; read with `port.read(64)` appending until the buffer ends with `b">"`; an empty read before the prompt → `AdapterNoResponse(c)`. Decode ASCII (errors="replace"), drop the final `>`, treat `\n` as `\r`, split on `\r`, strip each line, drop empty lines, drop the first line if its whitespace-free upper-case form equals `c` (echo). `log.rx(line)` for each remaining line. Return the list.
- `open()`: `port.reset_input_buffer()`, then `send` each INIT command; `ATZ` reply must contain a line containing `ELM327`, every other INIT reply must contain `OK`; otherwise `ProtocolError`. `AdapterNoResponse` propagates.
- `close()`: `port.close()`.
- `elm_parse.parse_response(lines) -> list[EcuReply]`: skip empty lines and `SEARCHING...`; remember `NO DATA`; a line equal to `?` or containing any of `UNABLE TO CONNECT`, `CAN ERROR`, `BUS ERROR`, `ERROR`, `STOPPED`, `BUFFER FULL`, `FB ERROR`, `DATA ERROR` → `ProtocolError`. Data lines: tokens split on whitespace; first token of 3 hex chars = 11-bit header; else if ≥ 5 tokens and the first four are 2-hex-char tokens = 29-bit header (joined, e.g. `18DAF110`); else `ProtocolError`. Remaining tokens must all be 2 hex chars and at least one, else `ProtocolError`. PCI high nibble 0: single frame, length = low nibble (1..7), fewer bytes than length → `ProtocolError`, extra bytes ignored (padding). 1: first frame, length = (low nibble << 8) | next byte, start assembly for that header. 2: consecutive frame; no assembly for header → `ProtocolError`; sequence nibble must equal expected (1,2,…,15,0,…) else `ProtocolError`; append; when ≥ length, emit trimmed reply. Other nibbles → `ProtocolError`. After all lines: any unfinished assembly → `ProtocolError`; no replies and `NO DATA` seen → `NoData`; no replies otherwise → `ProtocolError`. Replies are returned in completion order. Tests: T-U13..T-U20, T-P01.

### D-013 decoders
- `dtc.decode_dtc(two)`: length ≠ 2 → `ProtocolError`; letter `"PCBU"[b0>>6]`, then `(b0>>4)&3`, then hex digits of `b0&0xF`, `b1>>4`, `b1&0xF` (upper-case).
- `dtc.parse_dtc_list(payload, service)`: `len(payload) < 2` or `payload[0] != service + 0x40` → `ProtocolError`; `rest = payload[2:]` (byte 1 is the count, not checked); odd length → `ProtocolError`; decode pairs, skipping `00 00`.
- `pids.decode_pid(pid, data)`: pid not in `PID_TABLE` → `UnsupportedPid`; `len(data)` ≠ table length → `ProtocolError`. Formulas (A = data[0], B = data[1]): 04 `A*100/255` (float); 05 `A-40` (int); 0B `A` (int); 0C `(256A+B)/4` (float); 0D `A` (int); 0E `A/2-64` (float); 0F `A-40` (int); 11 `A*100/255` (float); 1C `A` (int); 21 `256A+B` (int); 42 `(256A+B)/1000` (float). Returns `Reading(pid, name, value, unit)` using table name/unit.
- `pids.monitor_status(data)`: length ≠ 4 → `ProtocolError`; `MonitorStatus(mil=bool(A & 0x80), dtc_count=A & 0x7F)`.
- `pids.supported_pids(bitmaps)`: each value length ≠ 4 → `ProtocolError`; bit i (MSB first, i = 0..31) set → PID `base + i + 1`.
- `vehicle.decode_vin(payload)`: `payload[:2] != 49 02` → `ProtocolError`; take `payload[3:]`, strip `\x00` both ends, ASCII decode; must match `[A-HJ-NPR-Z0-9]{17}` else `ProtocolError`.
- `vehicle.redact_vin(vin)`: length ≠ 17 → `ValueError`; `vin[:3] + "*"*8 + vin[-6:]`.
Tests: T-U01..T-U12, T-U21..T-U23.

### D-014 session.DiagSession(transport)
`LOW_VOLTAGE_THRESHOLD = 12.0`. All vehicle queries go through `parse_response(transport.send(cmd))`.
- `probe()`: in this order: `ATRV` (first line, strip trailing `V`/`v`, `float`), `0100` (headers of replies, sorted, unique), `ATDPN` (first line, leading `A` removed), `ATDP` (first line stripped; leading `AUTO, ` removed). If voltage < threshold: `warnings.warn(LowVoltageWarning(...))`, `low_voltage=True`. `NoData`/`ProtocolError` from `0100` propagate.
- `read_dtcs(kind)`: kind not in `DTC_SERVICES` → `ValueError`; send `f"{service:02X}"`; `NoData` → `{}`; else `{header: parse_dtc_list(data, service)}`.
- `read_pids(pids)`: every pid must be in `PID_TABLE` (else `UnsupportedPid`, before sending anything); for each pid send `f"01{pid:02X}"`; `NoData` → skip pid; each reply must start `41 <pid>` else `ProtocolError`; append `decode_pid(pid, data[2:])` under its header. Returns only headers that answered.
- `read_supported_pids()`: base = 0x00; loop: send `f"01{base:02X}"` (`NoData` → stop); union `supported_pids({base: data[2:6]})` over replies; continue with base+0x20 only if PID base+0x20 is in the set and base < 0xE0.
- `read_monitor_status()`: `0101` → `{header: monitor_status(data[2:])}`.
- `read_vehicle_info()`: `0902` → `decode_vin(first reply)` or `None` on `NoData`; `0904` → split `data[3:]` into 16-byte chunks, right-strip `\x00`, ASCII decode → list (empty on `NoData`); `090A` → `data[3:]` right-stripped of `\x00`, ASCII, or `None` on `NoData`.
Tests: T-I01..T-I06, T-O06.

### D-015 transcript.TranscriptLog(path, clock=None)
Opens `path` in append mode, UTF-8. `clock()` returns an aware `datetime` (default `datetime.now(timezone.utc)`). `tx(text)` / `rx(text)` write `f"{clock().isoformat()} TX {text}\n"` / `RX`, flush each line. `close()` idempotent. Test: T-I07.

### D-016 report
`build_report(*, probe, dtcs, readings, info, monitor, now, redact_vin=True)` returns exactly:
`schema_version` ("1"), `generated_at` (`now.isoformat()`), `tool_version` (`tracer_diag.__version__`), `adapter` {`protocol_number`, `protocol_name`, `voltage`, `low_voltage`}, `ecus` (list), `vehicle` {`vin` (redacted unless `redact_vin=False`; `None` if unknown), `vin_redacted` (`True` only when a VIN exists and was redacted), `calibration_ids`, `ecu_name`}, `monitor` {header: {`mil`, `dtc_count`}}, `dtcs` {`stored`,`pending`,`permanent`: {header: [codes]}} (missing kinds → `{}`), `readings` {header: [{`pid`: `"0x%02X"`, `name`, `value`, `unit`}]}. Every string originating from the vehicle has characters < 0x20 and 0x7F–0x9F removed.
`write_report(report, path)`: `tempfile.mkstemp(dir=<dir of path>, suffix=".tmp")`, then `os.fdopen(fd, "w", encoding="utf-8")`; `json.dump(report, f, indent=2, sort_keys=True)` (call `json.dump` through the module-level `json` import); flush, `os.fsync`, `os.replace(tmp, path)`; on any exception delete the temp file and re-raise.
`render_text(report)`: header line with tool version and timestamp; `Protocol: <name>  Voltage: <v> V`; one line per ECU `ECU <hdr> MIL: ON|OFF (<n> DTCs)`; then for each of stored, pending, permanent: `<kind>: <codes joined by ", ">` or `<kind>: none`. Tests: T-U24..T-U26, T-S10, T-O08.

### D-017 cli.main(argv=None, *, transport_factory=None, clock=None, sleep=None) -> int
Exit codes: 0 OK, 2 usage, 3 adapter, 4 vehicle, 130 interrupted.
Global options: `--port` (else env `TRACER_DIAG_PORT`), `--baud` (int, 115200), `--timeout` (float, 5.0), `--transcript PATH`. Subcommands (argparse, required): `probe`; `dtc [--kind stored|pending|permanent|all]` (default all); `live [--pids 0C,05,0D,11] [--hz 5] [--duration 10] --csv PATH`; `info [--show-vin]`; `report --out PATH [--show-vin] [--text]`. No other subcommands; help text must not contain the words clear, erase, flash or reset.
- argparse `SystemExit` → return its code (help → 0, errors → 2).
- No port → stderr message containing `--port`, return 2.
- Default factory: `ElmTransport(open_serial(port, baud, timeout), timeout=timeout, log=TranscriptLog(path) if --transcript)`. Injected factory is called as `transport_factory(port, baud, timeout)` and returns an unopened transport. The CLI calls `open()` then builds `DiagSession`.
- `probe`: prints `protocol <n>: <name>`, `voltage <v> V`, `ecus <headers space-separated>`.
- `dtc`: prints `<kind>: <codes>` or `<kind>: none` for the selected kinds in order stored, pending, permanent.
- `info`: prints `vin: <redacted|full|none>`, `calibration_ids: <comma list|none>`, `ecu_name: <name|none>`.
- `report`: probe → monitor → dtcs (3 kinds) → supported PIDs → `read_pids(sorted(PID_TABLE ∩ supported))` → vehicle info → `build_report(now=datetime.now(timezone.utc))` → `write_report(--out)`; `--text` also prints `render_text`.
- `live`: parse `--pids` as hex (ValueError → stderr, return 2); unknown PID → `UnsupportedPid` → stderr naming it (`0x5C`), return 2, before any mode-01 query. Open the CSV with `open(path, "w", encoding="utf-8", newline="")` (identical bytes on Windows and Linux) and write the header `t,<names>` plus `\n`, flush, before polling. `start = clock()`; loop: `now = clock()`; stop if `now - start >= duration`; `read_pids`; row = `str(now)` then for each PID `str(value)` from the first header (sorted) that has it, else empty; write, flush; `sleep(1.0 / hz)`. `clock` defaults to `time.monotonic`, `sleep` to `time.sleep`; the CLI calls `clock` nowhere else.
- Exceptions: `KeyboardInterrupt` → 130; `AdapterNotFound`/`AdapterNoResponse` → stderr, 3; `NoData`/`ProtocolError` → stderr containing "ignition", 4; `UnsupportedPid` → 2. The transport is closed in `finally` whenever it was created, and the `TranscriptLog` (if any) is closed after it. All console output is ASCII.
Tests: T-I08..T-I10, T-S08, T-S09, T-O01..T-O03, T-O05, T-O07, T-O09, T-O10, T-P02.

### D-018 capture (stretch; `pip install .[capture]`)
`open_listen_only(channel, *, interface="slcan", bitrate=500000)`: interface not in {slcan, virtual} → `UnsafeCommand`. slcan: `can.Bus(interface="slcan", channel=channel, bitrate=bitrate, listen_only=True)`; virtual: `can.Bus(interface="virtual", channel=channel)`. Call `can.Bus` via the module attribute (`import can`). Return a wrapper exposing `recv(timeout=None)` and `shutdown()` that delegate, and `send(...)` that raises `UnsafeCommand`.
`capture(bus, duration_s, out_path, clock=None)`: `clock` default `time.monotonic`; `start = clock()`; while `clock() - start < duration_s`: `m = bus.recv(timeout=0.05)`; if `m`: write `f"({m.timestamp:.6f}) can0 {ID}#{DATA}\n"` (ID `%03X`, or `%08X` if extended; DATA upper-case hex), flush, count. Returns the count.
`summarize(path)`: `{ID: count}` from the third field of each line. Tests: T-U27, T-S11, T-S12.

### D-019 Performance budgets
T-P01 10,000 lines < 1.0 s; T-P02 ≥ 400 PIDs/s software throughput (2× OBDLink EX's ~200 PIDs/s, C-011). Measured medians in spike S6: 0.038 s and 0.011 s (≥ 26× headroom), so budgets hold on slower laptops.

### D-020 Test satisfiability evidence
A throwaway reference implementation passed all 174 frozen test cases in the planning sandbox and was discarded (spike S7). The implementer builds from this document, not from that code.

### D-021 Tier substitution
No subagent spawning here. Every role (Haiku/Sonnet/Opus/Fable) was performed sequentially by the planning agent (Fable/Mythos-class). Logged in `.checkpoints/state.json.tier_substitutions`. The implementer should use the tiers named in each step if available (Global Rule 5 otherwise).

## Decision rules (if → then)
- **DR-01** Dependency install fails → retry once; confirm `python --version` is 3.12.x. Hash mismatch → halt, `BLOCKED.md` (supply-chain integrity).
- **DR-02** A frozen test looks wrong → do not edit it; write `TEST_CHALLENGE.md` (test ID, evidence, proposed fix) and halt.
- **DR-03** `pip-audit` reports a vulnerability → if a fixed version exists: bump the pin in `requirements*.in`, re-run `pip-compile --strip-extras --generate-hashes --allow-unsafe`, run the full suite, log in `DEVIATIONS.md`. No fix available → halt, `BLOCKED.md`.
- **DR-04** A performance test fails → profile and optimise the code; never change the budget; if still failing after two attempts, halt `BLOCKED.md`.
- **DR-05** Outcome of the G-003 on-bike probe (human reports; implementer applies):
  a) protocol 6 or 8 (CAN 11-bit) and ECU 7E8 answers → proceed.
  b) protocol 7 or 9 (29-bit) → proceed (parser supports it).
  c) protocol 3, 4 or 5 (K-line) → proceed; set `live` usage guidance to `--hz 2` in README.
  d) `UNABLE TO CONNECT` / `NO DATA` with pin 16 at 11.5–14.5 V → reseat the lead, retry once; still failing → stop at G-003 with options: (i) a second lead from a different seller, (ii) dealer YDT check that the ECU answers OBD, (iii) stretch passive capture (G-004) to see whether the port carries CAN at all.
  e) pin 16 outside 11.5–14.5 V, or `ATRV` < 11.0 V → adapter unpowered or lead miswired → stop; do not try other leads until measured.
  f) any warning lamp change or abnormal bike behaviour → disconnect, stop, record.
- **DR-06** Real adapter text differs from FakeElm and parsing fails → collect the VIN-redacted transcript excerpt, write `TEST_CHALLENGE.md`, halt (protocol re-run from Phase 0).
- **DR-07** Bluetooth link drops (`AdapterNoResponse` mid-session) → re-pair and retry once; if it recurs, lower `--hz` to 2; if still recurring, record and recommend the USB EX (rank 2) at the next G-002.
- **DR-08** At purchase: MX+ + lead > £150, or the human confirms Windows-only use → buy rank 2 (EX + lead). Lead must say ISO 19689 / Euro 5 red 6-pin and CAN + K-line; otherwise pick another seller.
- **DR-10** At G-003 the bike shows a white 4-pin connector instead of the red 6-pin (C-001 wrong) → stop; next G-002a buys a Yamaha 4-pin→16-pin lead (pre-2021 bikes use CAN 11/500 on it, C-006); the software is unchanged.
- **DR-09** Security scan (CHK-03) finds a token or VIN in tracked files → remove it, rewrite the commit before pushing, and tell the human to rotate the token; halt if already pushed.
- **Default rule:** choose the most reversible option that does not expand scope, log it in `DEVIATIONS.md`, continue — unless it touches frozen tests, security, data integrity, a public interface, or research integrity; then halt and write `BLOCKED.md`.
