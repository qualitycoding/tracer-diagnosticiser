# Pre-mortem round 1

Reviewer: planning agent in a fresh adversarial role (no subagents available, D-021 / R-020). Lenses: technical correctness, dependency drift, research assumptions (every single-source/inferred claim), implementer misinterpretation, integrity, scale/performance, security, operations.

## Incident report (6 months after "release", despite perfect adherence)
The owner bought an OBDLink MX+ and a 6-pin lead. The lead's pin 16 was unconnected on a cheap listing, the adapter stayed dark, and a second attempt with another lead reached the ECU but the Windows CSV logs had blank lines between rows and one `live` session ended with "Access denied" on COM5 because an Android app was still paired and connected. In parallel the plan's public repo briefly carried a report with the full VIN from an early test that bypassed `runs/`, and the owner never rotated the GitHub token pasted during planning. A later contributor, asked to "add a clear-codes button", widened the allowlist in the same commit as a refactor.

## Failure modes found (→ RISK_REGISTER.md)
- R-001 ECU does not answer generic OBD (C-005 inferred) — High.
- R-002 miswired/unsuitable lead (C-003 single-source) — High.
- R-003 mutating command reaches the ECU (C-022) — Critical.
- R-006 PAT exposure — Critical.
- R-017 VIN in the public repo — High.
- R-021 Windows-specific defects (CSV newlines, encodings, COM contention) — High.
- R-011 Bluetooth link loss / COM held by another device — Medium.
- R-018 connector differs from C-001 — High (implementer blocked).
- R-020 weakened review independence — Medium.
- plus Medium/Low items R-004, R-005, R-007, R-009, R-010, R-012..R-016, R-019, R-022..R-024.

## Hardening applied in this round
- D-017: CSV opened with `newline=""` and UTF-8; transcript closed in `finally`; ASCII console output (R-021).
- D-016: report written through `os.fdopen(..., encoding="utf-8")` (R-021).
- DR-10 added for a 4-pin connector (R-018).
- HANDOFF §6: pin-16 measurement before connecting the adapter; "no other OBD devices" and disconnect-other-phone instruction (R-002, R-011).
- CHK-03 checks for tokens and tracked `runs/`; `.gitignore` excludes reports, CSVs, transcripts (R-006, R-017).
- A-016: human to rotate the PAT (R-006).
- T-S02/T-S04/T-S08 already frozen; D-011 default-deny; any allowlist change is a public-interface/security change → `BLOCKED.md` (R-003).
Tests were not yet frozen when these changes were made, so no unfreeze was needed; the cold-read gate was re-run afterwards (research/rounds/cold-read.md pass 2).

Critical/High remaining after mitigation: 0 (see residual severities in the register). A second round is still required to confirm.
