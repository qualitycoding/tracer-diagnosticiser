# Research round 3 — adversarial pass (R5) + saturation check

Adversarial queries: "MT-09 2021 6 pin OBD adapter ELM327 no data not connecting"; clone ELM327 failures; OBDLink MX+ Windows COM pairing; US vs EU variant differences.
Attempts to disprove load-bearing claims:
- C-005: found region-dependent failures on pre-2021 4-pin bikes (S18, Canada) and generic clone limitations (S23) — not a contradiction for a UK Euro 5 bike, but kept `inferred`; mitigations A-007, D-001, DR-05.
- C-003/C-004: found vendors noting the tool must itself support the protocol (S30) — consistent.
- C-011/C-012: vendor pages consistent across documents.
- C-022 (write capability of the port) confirmed by a tuner (S24) — strengthens D-011.
Also found: PAT exposure risk (credential pasted in chat) → R-006, CHK-03.
Platform change from intake (A-008 Windows or Android + Bluetooth) re-ran the hardware ranking (HARDWARE.md v2) — no new load-bearing claims beyond C-012.
Saturation: this round produced no new load-bearing claims, no downgrades, no unresolved contradictions. Research stops at round 3 (minimum met). Load-bearing claims still below `corroborated` (C-001, C-003, C-005, C-007, C-019, C-022) are carried to `premortem/RISK_REGISTER.md`.
