# Pre-mortem round 2

Reviewer role: fresh adversarial pass over the hardened plan (same agent, new role; D-021).

## Incident report
Twelve months on, the tool works on the owner's Windows laptop, but the owner expected ABS and suspension fault codes and felt the project failed; separately, a firmware update on the adapter changed the `ATZ` banner.

## Findings
- ABS/suspension expectation gap → R-019 (Medium; C-007 documented in HARDWARE.md and README; stretch path G-004).
- Banner change: D-012 requires a line containing `ELM327`; OBDLink firmware prints `ELM327 v1.4b` for compatibility (C-011 family docs). If it ever changes, DR-06 → TEST_CHALLENGE (fixture) — R-015 Medium.
- Re-checked every Critical/High from round 1: all have a defensive control or gate; none rely on a single-source claim without a gate.
- Implementer misinterpretation lens: selectors in S-006/S-007 were ambiguous (fixed during cold-read pass 1).
- Integrity lens: no hand-typed results; oracle values come from committed spikes; refimpl evidence recorded without committing code (D-020).

Critical: 0. High: 0. Round limit not reached; iteration stops (Phase 4.5).
