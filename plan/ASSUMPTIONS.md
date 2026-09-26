# Assumptions and intake answers

Intake batch answered by the human on 2026-09-26 (only question round). "default" = proposed default adopted.

| ID | Topic | Resolution | Source | Consequence |
|---|---|---|---|---|
| A-001 | Execution mode | Full protocol. GitHub push works (PAT supplied in chat, used only via an HTTP header in the planning sandbox, never written to the repo). Subagents are unavailable, so every "fresh agent" pass is a role-separated sequential self-review by the planning agent (D-021). | human: "do the full thing" | Cold-read and pre-mortem independence is weaker than specified → R-020. |
| A-002 | Repository | `https://github.com/qualitycoding/tracer-diagnosticiser` (public, empty at start). Generation branch `gen-20260926T164526Z-tracer9gt-obd-reader`; implementation branch `impl/tracer-diag`. | human | Everything pushed is public → no VIN, transcripts or secrets committed (R-006, R-017). |
| A-003 | Goal | Read the bike's diagnostics with self-built software; ranked hardware selection is the first deliverable (mirrors the Renault-diagnosticiser project). | default | Profile `software`. |
| A-004 | Profiles | `software` only, `software.deploys = false`. | default | See PROFILE.md. |
| A-005 | Read/write boundary | Read-only "for now": fault codes, freeze-frame, live data, vehicle info. No clearing codes, no flashing, no service resets, no calibration writes. | human: "RO for now" | D-011 default-deny allowlist; no clear subcommand (T-S08). A future write feature needs a new protocol run. |
| A-006 | Modules | Engine ECU required. ABS, IMU, semi-active suspension, dash: stretch, investigated only passively after G-004. The human confirms they own the bike and can do on-bike checks. | human: "I have the bike" + default | SC-1..SC-6 target the engine ECU; SC-7 is stretch. |
| A-007 | Market variant | UK-specification Euro 5 2022 Tracer 9 GT. | human: "uk" | Evidence from EU/UK sources applies; US-spec differences irrelevant. |
| A-008 | Host platforms | Windows laptop, or Android phone over Bluetooth. Own software targets Windows 10/11 (Python 3.12, COM port over USB or Bluetooth SPP) and also runs on Linux. Android is served by third-party ELM327 apps (no custom Android software). | human | Ranking re-scored for platform fit (HARDWARE.md); D-006, D-012. |
| A-009 | Budget | £150 ceiling for the primary purchase (adapter + lead); pricier tools ranked for reference only. | default | Tie-break and budget rule DR-08. |
| A-010 | Ranking method | Pass/fail gate on credible support for a 2022 Tracer 9 GT; then weights: openness for own code 30 %, cost 20 %, diagnostic depth 20 %, platform fit 15 %, safety/vendor support 15 %. Scores 1–5. | default | Ties within 0.10 broken by coverage of A-008 platforms (D-007). |
| A-011 | Owned hardware | None. | human | Primary purchase = adapter + ISO 19689 lead. |
| A-012 | Purchases and bike work | Every purchase passes G-002. On-bike checks: ignition ON, engine OFF, bike on a stand, performed by the human, never by an agent. | human: "agreed" | G-002, G-003, G-004. |
| A-013 | Implementer environment | The implementing agent works on Linux (Ubuntu 24.04 or similar) with Python 3.12 and git; it never touches the bike. Windows behaviour is validated by the human at G-003. | planning default | R-021 (Windows-only defects found late). |
| A-014 | Licence | No licence file is added by the plan; the human chooses one at G-002b before merging to `main`. | planning default | Public repo without licence until then. |
| A-015 | Android apps | For Android use, the plan names read-capable apps (Car Scanner ELM OBD2, OBDLink app) but cannot enforce read-only there; the human must not use their clear functions (A-005). | planning default | R-022. |
| A-016 | Credential hygiene | The PAT pasted in chat should be revoked or rotated by the human after this run; it is not needed by the implementer beyond pushing branches. | planning default | R-006. |
