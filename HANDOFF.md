# HANDOFF — tracer-diagnosticiser

## 1. Purpose
Build `tracer-diag`, a **read-only** Python tool that reads engine diagnostics (DTCs, MIL, live PIDs, VIN/CALID) from a UK 2022 Yamaha Tracer 9 GT through its red ISO 19689 6-pin port, an ISO 19689→J1962 lead and an OBDLink adapter; and validate the ranked hardware choice on the bike via human gates.

## 2. Active profile
`software` only, `software.deploys = false` (plan/PROFILE.md).

## 3. Reading order
1. `plan/PLAN.md` (status, success criteria, checks, steps)
2. `plan/DECISIONS.md` (normative interfaces D-010..D-018, decision rules DR-01..DR-09)
3. `plan/GATES.md`
4. `plan/HARDWARE.md`
5. `plan/ENVIRONMENT.md`, `plan/ASSUMPTIONS.md`, `plan/TRACEABILITY.md`
6. `premortem/RISK_REGISTER.md`; research in `research/` for background only.

## 4. Environment, frozen suite, freeze manifest
See `plan/ENVIRONMENT.md` §Implementer setup. Run the frozen suite with `python -m pytest -q` (174 cases; red at hand-off). Verify the freeze with `sha256sum -c tests/FROZEN_MANIFEST.sha256` (every line `OK`). The manifest also covers `tests/fixtures/fake_elm.py` and `tests/conftest.py`.

## 5. Steps at a glance
S-001 setup → S-002 allowlist → S-003 parser → S-004 decoders → S-005 transport/transcript → S-006 session → S-007 report → S-008 CLI → S-009 capture → S-010 checks + README → **S-011 G-002a purchase** → **S-012 G-003 on-bike (human)** → **S-013 G-002b merge** → S-014 stretch (**G-004**).

Gates: G-002a (purchase), G-003 (first on-bike session), G-002b (merge to public main), G-004 (stretch). G-001 N/A. The agent never buys, never touches the bike, never merges.

## 6. G-003 checklist (copy into `GATE-G-003.md`; the human fills it in)
Safety first: bike on a stand, engine OFF, ignition ON only while measuring or reading, no splitters, no other OBD devices connected. Stop immediately if any warning lamp changes.
1. Locate the red 6-pin diagnostic connector using the owner's manual section "Diagnostic connector". Record where it is: ______
2. Confirm it is red and 6-pin (not the older white 4-pin): yes/no
3. Plug in the ISO 19689 lead only (no adapter yet). Ignition ON. Measure pin 16 to pin 4 (or 5) on the 16-pin end: ____ V (must be 11.5–14.5 V; otherwise DR-05e → stop). Ignition OFF.
4. Plug the adapter into the lead. For MX+: pair per `plan/ENVIRONMENT.md` §Bluetooth and note the COM port: COM__. For EX: note the USB COM port: COM__.
5. Ignition ON. `mkdir runs` then:
   - `tracer-diag --port COMn --transcript runs\probe.log probe` → paste output
   - `tracer-diag --port COMn dtc` → paste output
   - `tracer-diag --port COMn report --out runs\report.json --text` → paste the text (VIN is redacted)
   - `tracer-diag --port COMn live --duration 30 --hz 2 --csv runs\live.csv` → number of data rows: ____
6. Did any warning lamp, dash message or bike behaviour change? ____ Did Bluetooth disconnect? ____
7. Are coolant temperature, RPM (0 with engine off) and module voltage plausible? ____
8. Ignition OFF, disconnect. Do **not** commit anything in `runs\`.
Reply `proceed`, `proceed-with-rescope: <text>` or `stop`. The implementer applies DR-05.

## 7. Halt / deviation protocol
- Unanticipated situation → apply the default rule in `plan/DECISIONS.md`; log in `DEVIATIONS.md`.
- Frozen test invalid → `TEST_CHALLENGE.md`, halt (DR-02/DR-06).
- Security, data integrity, public interface or supply-chain problem → `BLOCKED.md`, halt.
- Never modify, skip, xfail or weaken a frozen test. Never add a command that clears or writes (A-005). Never commit VINs, transcripts or tokens (CHK-03).

## 8. Integrity rule (Rule 9, verbatim)
**Integrity** `[All]`: No step may fabricate, cherry-pick without disclosure, or manually alter data, test results, benchmarks, or figures.

## 9. Deployment
None (`software.deploys = false`); no `plan/OPERATIONS.md`.

## 10. Credentials
- **Implementer:** push access to `github.com/qualitycoding/tracer-diagnosticiser` (fine-grained token, repository contents: read/write; pull requests: read/write for S-013). Provide it via the git credential helper or `GH_TOKEN`; never write it into any file (CHK-03). No other credentials exist; there is no staging target.
- **Human:** rotate the token that was pasted into the planning chat (A-016).
