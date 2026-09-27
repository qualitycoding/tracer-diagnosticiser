# Gate G-002a — hardware purchase

Trigger: step S-011 (plan/PLAN.md). Implementation (S-001–S-010) is complete: 174/174 tests pass,
all four checks (CHK-01..CHK-04) pass. See `plan/HARDWARE.md` for the full ranking and reasoning.

## Recommended purchase
1. **OBDLink MX+** (Bluetooth) — works with both your Windows laptop and your Android phone.
2. A moulded **ISO 19689 6-pin (red, Euro 5) → SAE J1962 16-pin** adapter lead, from a listing that
   explicitly names "ISO 19689" or "Euro 5 6-pin" **and** states it carries CAN and K-line.

**Fallback (DR-08):** if the MX+ + lead together exceed £150, or you decide you'll only ever use the
Windows laptop, buy the **OBDLink EX** (USB) instead — same lead, same software, no Bluetooth pairing
step at G-003.

**Do not buy:** Yamaha 3-pin/4-pin leads (wrong connector for this bike), any "MIL eliminator" or
code-clearing gadget (this project is read-only by design), or a splitter (C-021 — it can cause the
adapter to see "no data").

## Question
Buy the OBDLink MX+ and the ISO 19689 lead (or the EX per the fallback above)? What did they actually
cost, and which did you buy?

Reply `proceed` (record what you bought), `proceed-with-rescope: <text>`, or `stop`.

## Evidence bundle
- Ranking table and scoring notes: `plan/HARDWARE.md`.
- DR-08 tie-break rule: `plan/DECISIONS.md`.
- Test suite: 174 passed, 0 failed (`python -m pytest -q` on branch `impl/tracer-diag`).
- CHK-01 (`pip-audit`): no known vulnerabilities in `requirements.txt` or `requirements-dev.txt`.
- CHK-02 (freeze): `sha256sum -c tests/FROZEN_MANIFEST.sha256` — all `OK`.
- CHK-03 (secrets/VIN): no token pattern found; no files under `runs/` tracked.
- CHK-04 (consistency): `CONSISTENT: 61 test IDs, 23 claims, 14 steps, 25 risks`.
