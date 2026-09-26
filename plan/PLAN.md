<!-- STATUS HEADER (Phase 5.2) -->
**STATUS: READY**
- Active profiles: `software` (`software.deploys = false`)
- Claims: 23 total — verified 5, corroborated 5, single-source 12, inferred 1 (load-bearing below corroborated: 6, all carried as risks)
- Tests (frozen, red at freeze): 59 IDs / 174 cases — unit 27 IDs, integration 10, operational 10, security 12, performance 2; checks CHK-01..CHK-04
- Steps: 14 (S-001–S-014)
- Gates: 4 applicable (G-002a, G-002b, G-003, G-004); G-001 N/A
- Risks after mitigation: Critical 0, High 0, Medium 9, Low 13

# Execution Plan — read-only diagnostics for a 2022 Yamaha Tracer 9 GT (UK)

Implementation happens on `impl/tracer-diag`, created from the generation branch. Tests are frozen: never modify, skip, xfail or weaken them. Deviations go in `DEVIATIONS.md`, blockers in `BLOCKED.md`, invalid tests in `TEST_CHALLENGE.md`.

**Resume rule:** on restart read `.checkpoints/impl_state.json`, skip steps listed in `done`, re-run the first missing one. Every step only rewrites its own outputs, so re-running is safe.

## Success criteria
- **SC-1** `probe` reports adapter voltage, detected protocol and answering ECU headers.
- **SC-2** Stored, pending and permanent DTCs and MIL status are decoded.
- **SC-3** Supported live PIDs are discovered, decoded and logged to CSV at a set rate.
- **SC-4** VIN, calibration IDs and a JSON report (schema v1, atomic write) plus a text summary.
- **SC-5** Clear exit codes/messages for missing port, dead adapter, silent vehicle, low voltage, Ctrl-C.
- **SC-6** No clearing or writing command can reach the adapter; VIN redacted by default.
- **SC-7** (stretch) Any multi-module discovery is passive or read-only and gated (G-004).
- **SC-8** A raw TX/RX transcript can be recorded for every session.
- **SC-9** A ranked, evidence-backed hardware recommendation exists and is validated on the bike (HARDWARE.md, G-003).
- **SC-10** Runs on Windows 10/11 with a USB or Bluetooth COM port (validated at G-003).

## Checks
- **CHK-01 (dependency scan):** `pip-audit -r requirements.txt && pip-audit -r requirements-dev.txt` → exit 0.
- **CHK-02 (freeze):** `sha256sum -c tests/FROZEN_MANIFEST.sha256` → every line `OK`.
- **CHK-03 (secrets/VIN):** `git grep -nIE "github_pat_[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9]{30,}"` → no output (exit 1); `git ls-files runs` → no output.
- **CHK-04 (consistency):** `python research/spikes/consistency_check.py` → prints `CONSISTENT` and exits 0.

## Steps

### S-001 Environment setup and freeze verification
- Tier: Sonnet
- Profile: software
- Depends on: none
- Inputs: repo checkout of `gen-20260926T164526Z-tracer9gt-obd-reader`
- Actions:
  1. `git fetch origin && git checkout -b impl/tracer-diag origin/gen-20260926T164526Z-tracer9gt-obd-reader` (if `impl/tracer-diag` already exists remotely: `git checkout -b impl/tracer-diag origin/impl/tracer-diag`)
  2. Run every command in `plan/ENVIRONMENT.md` §Implementer setup.
  3. Create `.checkpoints/impl_state.json` with `{"done": []}` if absent.
  4. `python -m pytest -q` must print `174 failed` and no errors.
- Outputs: `.venv/` (untracked), `.checkpoints/impl_state.json`
- Evidence produced: none
- Done when: CHK-02 all OK; pytest summary `174 failed`, 0 errors
- Checkpoint: append `S-001` to `.checkpoints/impl_state.json` `done`; commit `impl: S-001 Environment setup and freeze verification`; `git push origin impl/tracer-diag`
- On failure: DR-01; manifest mismatch → halt `BLOCKED.md`.
- Gate: none
- Relevant decisions/claims: D-006, C-020

### S-002 Read-only allowlist
- Tier: Opus
- Profile: software
- Depends on: S-001
- Inputs: src/tracer_diag/safety.py, plan/DECISIONS.md D-011
- Actions:
  1. Implement `check_command` exactly as D-011 (keep the three module constants unchanged).
  2. `python -m pytest -q tests/security/test_safety.py -k "T_S01 or T_S02 or T_S03 or T_S04 or T_S05"`
- Outputs: src/tracer_diag/safety.py
- Evidence produced: T-S01..T-S05
- Done when: those tests pass; CHK-02
- Checkpoint: append `S-002` to `.checkpoints/impl_state.json` `done`; commit `impl: S-002 Read-only allowlist`; `git push origin impl/tracer-diag`
- On failure: Retry once; else `BLOCKED.md`. Never widen the allowlist to make a test pass (security).
- Gate: none
- Relevant decisions/claims: D-011, C-022, A-005

### S-003 ELM response parser
- Tier: Sonnet
- Profile: software
- Depends on: S-001
- Inputs: src/tracer_diag/elm_parse.py, D-012
- Actions:
  1. Implement `parse_response` per D-012.
  2. `python -m pytest -q tests/unit/test_elm_parse.py tests/performance/test_performance.py::test_T_P01_parse_throughput`
- Outputs: src/tracer_diag/elm_parse.py
- Evidence produced: T-U13..T-U20, T-P01
- Done when: those tests pass; CHK-02
- Checkpoint: append `S-003` to `.checkpoints/impl_state.json` `done`; commit `impl: S-003 ELM response parser`; `git push origin impl/tracer-diag`
- On failure: Retry once; DR-04 for T-P01; else `BLOCKED.md`.
- Gate: none
- Relevant decisions/claims: D-012, C-020

### S-004 Decoders: DTC, PID, VIN
- Tier: Sonnet
- Profile: software
- Depends on: S-001
- Inputs: src/tracer_diag/dtc.py, pids.py, vehicle.py, D-013
- Actions:
  1. Implement all functions per D-013 (int vs float return types as listed).
  2. `python -m pytest -q tests/unit/test_dtc.py tests/unit/test_pids.py tests/unit/test_vehicle.py`
- Outputs: src/tracer_diag/dtc.py, pids.py, vehicle.py
- Evidence produced: T-U01..T-U12, T-U21..T-U23
- Done when: those tests pass; CHK-02
- Checkpoint: append `S-004` to `.checkpoints/impl_state.json` `done`; commit `impl: S-004 Decoders: DTC, PID, VIN`; `git push origin impl/tracer-diag`
- On failure: Retry once; else DR-02 if a test value seems wrong.
- Gate: none
- Relevant decisions/claims: D-013, C-014, C-015

### S-005 Transcript log and serial transport
- Tier: Sonnet
- Profile: software
- Depends on: S-002, S-003
- Inputs: src/tracer_diag/transcript.py, transport.py, D-012, D-015
- Actions:
  1. Implement `TranscriptLog` per D-015.
  2. Implement `open_serial` and `ElmTransport` per D-012 (check_command before every write).
  3. `python -m pytest -q -k "T_S06 or T_S07 or T_I07 or T_O03 or T_O04"`
- Outputs: src/tracer_diag/transcript.py, transport.py
- Evidence produced: T-S06, T-S07, T-I07, T-O03 (transport part), T-O04
- Done when: T-S06, T-S07, T-I07, T-O04 pass (T-O03 fully passes after S-008); CHK-02
- Checkpoint: append `S-005` to `.checkpoints/impl_state.json` `done`; commit `impl: S-005 Transcript log and serial transport`; `git push origin impl/tracer-diag`
- On failure: Retry once; else `BLOCKED.md`.
- Gate: none
- Relevant decisions/claims: D-012, D-015, C-012

### S-006 Diagnostic session
- Tier: Sonnet
- Profile: software
- Depends on: S-004, S-005
- Inputs: src/tracer_diag/session.py, D-014
- Actions:
  1. Implement `DiagSession` per D-014 (keep dataclasses and constant unchanged).
  2. `python -m pytest -q -k "T_I01 or T_I02 or T_I03 or T_I04 or T_I05 or T_I06 or T_O06"`
- Outputs: src/tracer_diag/session.py
- Evidence produced: T-I01..T-I06, T-O06
- Done when: those tests pass; CHK-02
- Checkpoint: append `S-006` to `.checkpoints/impl_state.json` `done`; commit `impl: S-006 Diagnostic session`; `git push origin impl/tracer-diag`
- On failure: Retry once; else `BLOCKED.md`.
- Gate: none
- Relevant decisions/claims: D-014, C-009

### S-007 Report
- Tier: Sonnet
- Profile: software
- Depends on: S-006
- Inputs: src/tracer_diag/report.py, D-016
- Actions:
  1. Implement `build_report`, `write_report`, `render_text` per D-016.
  2. `python -m pytest -q -k "T_U24 or T_U25 or T_U26 or T_S10 or T_O08"`
- Outputs: src/tracer_diag/report.py
- Evidence produced: T-U24..T-U26, T-S10, T-O08
- Done when: those tests pass; CHK-02
- Checkpoint: append `S-007` to `.checkpoints/impl_state.json` `done`; commit `impl: S-007 Report`; `git push origin impl/tracer-diag`
- On failure: Retry once; else `BLOCKED.md`.
- Gate: none
- Relevant decisions/claims: D-016, D-008

### S-008 Command-line interface
- Tier: Sonnet
- Profile: software
- Depends on: S-007
- Inputs: src/tracer_diag/cli.py, D-017
- Actions:
  1. Implement `main` per D-017.
  2. Create `src/tracer_diag/__main__.py` containing `import sys` / `from .cli import main` / `sys.exit(main())`.
  3. `python -m pytest -q` — everything except T-U27, T-S11, T-S12 must pass.
  4. `python -m tracer_diag --help` exits 0.
- Outputs: src/tracer_diag/cli.py, src/tracer_diag/__main__.py
- Evidence produced: T-I08..T-I10, T-S08, T-S09, T-O01..T-O03, T-O05, T-O07, T-O09, T-O10, T-P02
- Done when: pytest shows only the 3 capture tests failing; CHK-02
- Checkpoint: append `S-008` to `.checkpoints/impl_state.json` `done`; commit `impl: S-008 Command-line interface`; `git push origin impl/tracer-diag`
- On failure: Retry once; DR-04; else `BLOCKED.md`.
- Gate: none
- Relevant decisions/claims: D-017

### S-009 Passive capture module (stretch code, no bike use)
- Tier: Sonnet
- Profile: software
- Depends on: S-008
- Inputs: src/tracer_diag/capture.py, D-018
- Actions:
  1. Implement per D-018.
  2. `python -m pytest -q`
- Outputs: src/tracer_diag/capture.py
- Evidence produced: T-U27, T-S11, T-S12
- Done when: `174 passed`; CHK-02
- Checkpoint: append `S-009` to `.checkpoints/impl_state.json` `done`; commit `impl: S-009 Passive capture module (stretch code, no bike use)`; `git push origin impl/tracer-diag`
- On failure: Retry once; else `BLOCKED.md`.
- Gate: none
- Relevant decisions/claims: D-018, C-016

### S-010 Quality checks and user documentation
- Tier: Sonnet
- Profile: software
- Depends on: S-009
- Inputs: README.md, plan/HARDWARE.md, HANDOFF.md §6
- Actions:
  1. Run CHK-01, CHK-02, CHK-03, CHK-04 (see Checks).
  2. Update `README.md` §Usage with the Windows commands from `plan/ENVIRONMENT.md` and one example per subcommand; state that the tool is read-only; for Android state A-015 (apps named, never use their clear function).
  3. `python -m pytest -q` → `174 passed`.
- Outputs: README.md
- Evidence produced: none
- Done when: all four checks pass; `174 passed`
- Checkpoint: append `S-010` to `.checkpoints/impl_state.json` `done`; commit `impl: S-010 Quality checks and user documentation`; `git push origin impl/tracer-diag`
- On failure: DR-03 for CHK-01; DR-09 for CHK-03.
- Gate: none
- Relevant decisions/claims: A-008, A-015

### S-011 Hardware purchase decision
- Tier: Haiku
- Profile: software
- Depends on: S-010
- Inputs: plan/HARDWARE.md, DR-08
- Actions:
  1. Write `GATE-G-002a.md` with: recommended items (rank 1), fallback (rank 2) and the DR-08 test, required lead wording, and the question from plan/GATES.md.
  2. Commit, push, halt.
- Outputs: GATE-G-002a.md
- Evidence produced: none
- Done when: human replied per GATES.md; reply recorded in GATE-G-002a.md
- Checkpoint: append `S-011` to `.checkpoints/impl_state.json` `done`; commit `impl: S-011 Hardware purchase decision`; `git push origin impl/tracer-diag`
- On failure: n/a (human decision)
- Gate: G-002a
- Relevant decisions/claims: D-001, D-007, C-011, C-012

### S-012 First on-bike session (human-executed)
- Tier: Haiku
- Profile: software
- Depends on: S-011 and hardware delivered
- Inputs: HANDOFF.md §6 checklist
- Actions:
  1. Copy the HANDOFF.md §6 checklist into `GATE-G-003.md`.
  2. Commit, push, halt. The human runs the checklist on Windows and fills in results (VIN redacted; transcripts stay in `runs/`).
  3. On the human's reply apply DR-05; if DR-06 applies write `TEST_CHALLENGE.md`.
- Outputs: GATE-G-003.md
- Evidence produced: SC-1..SC-5, SC-9, SC-10 real-hardware evidence
- Done when: human reply received and DR-05 branch recorded
- Checkpoint: append `S-012` to `.checkpoints/impl_state.json` `done`; commit `impl: S-012 First on-bike session (human-executed)`; `git push origin impl/tracer-diag`
- On failure: DR-05, DR-06, DR-07
- Gate: G-003
- Relevant decisions/claims: C-001, C-003, C-005, D-003

### S-013 Merge to main
- Tier: Haiku
- Profile: software
- Depends on: S-012 (proceed)
- Inputs: test log, CHK outputs
- Actions:
  1. Re-run `python -m pytest -q`, CHK-01..CHK-04; paste outputs into `GATE-G-002b.md` with `git diff --stat main...impl/tracer-diag`.
  2. Commit, push, halt.
  3. After `proceed`: `gh pr create --base main --head impl/tracer-diag` (or give the human the compare URL) and add the licence file the human chose. The human merges.
- Outputs: GATE-G-002b.md
- Evidence produced: none
- Done when: human merged or answered
- Checkpoint: append `S-013` to `.checkpoints/impl_state.json` `done`; commit `impl: S-013 Merge to main`; `git push origin impl/tracer-diag`
- On failure: n/a
- Gate: G-002b
- Relevant decisions/claims: A-014

### S-014 Stretch: passive module discovery (optional)
- Tier: Sonnet
- Profile: software
- Depends on: S-013 and G-004 proceed
- Inputs: D-018, G-004
- Actions:
  1. Write `GATE-G-004.md` per GATES.md; halt.
  2. If `proceed`: add a README section describing `python -c` usage of `tracer_diag.capture` with an slcan adapter at 500 kbit/s, listen-only, output to `runs/`. The human runs it on the bike; no transmit path exists.
  3. UDS reads only if the human answered `proceed` (not `passive only`): expose `uds_read` through a new CLI flag — this changes a public interface → first halt with `BLOCKED.md` requesting a protocol re-run (scope change).
- Outputs: GATE-G-004.md, README.md
- Evidence produced: SC-7
- Done when: human reply recorded
- Checkpoint: append `S-014` to `.checkpoints/impl_state.json` `done`; commit `impl: S-014 Stretch: passive module discovery (optional)`; `git push origin impl/tracer-diag`
- On failure: Default rule
- Gate: G-004
- Relevant decisions/claims: A-006, C-007, C-016
