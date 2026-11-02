# Risk register

Severity per Global Rule 4 (`software` lines). "Residual" = after mitigation.

| ID | Description | Lens | Severity | Likelihood | Root cause | Traces to | Mitigation | Residual |
|---|---|---|---|---|---|---|---|---|
| R-001 | Engine ECU does not answer generic OBD through the 6-pin port | research assumption | High | Low–Medium | C-005 only Tier 2/4 | C-005, S-012 | Genuine STN adapter first (D-001); frozen DR-05 outcomes; MX+ also reads the owner's car, so the purchase is not stranded; fallbacks DR-05d | Medium |
| R-002 | Lead unsuitable/miswired (no +12 V, swapped CAN) | technical | High | Medium | C-003 no Tier 1 pinout | C-003, C-004, D-003 | Moulded lead naming ISO 19689 + CAN/K-line (DR-08); pin-16 measurement before adapter (HANDOFF §6.3); DR-05e | Low |
| R-003 | A clearing/writing command reaches the ECU | security | Critical | Low | ECU accepts writes via this port (C-022) | C-022, D-011 | Single chokepoint, default-deny allowlist; T-S01..T-S09 frozen; no clear subcommand; allowlist changes → BLOCKED | Low |
| R-004 | Battery drained during ignition-on sessions | operational | Medium | Medium | Ignition-on draw | D-014 | LOW_VOLTAGE_THRESHOLD warning (T-O06); ≤15 min sessions; maintainer | Low |
| R-005 | Clone adapter gives false negatives | research assumption | Medium | Medium | C-019 | C-019, D-001 | Rank 1–2 are STN-based; clones rank 3 only | Low |
| R-006 | GitHub PAT pasted in chat is exposed/abused | security | Critical | Medium | Credential shared in conversation | A-016, CHK-03 | Never written to repo or commits; CHK-03 token scan; human rotates the token (A-016); repo is public so scan before push (DR-09) | Medium |
| R-007 | Non-UK variant behaviour differs | research assumption | Medium | Low | C-006 regional reports | A-007 | Owner confirmed UK bike | Low |
| R-008 | UDS read requests (stretch) provoke unexpected behaviour in non-engine modules | security | High | Low | Requests sent to modules outside the engine ECU | D-011, G-004 | `uds_read` off by default (T-S05); no CLI flag exists; enabling it is a scope change requiring a protocol re-run (S-014) and G-004 | Low |
| R-009 | Implementer misreads semantics (live loop, report schema) | misinterpretation | High | Low | Complex spec | D-016, D-017 | Behaviour pinned by frozen tests; cold-read passes | Low |
| R-010 | Dependency drift / compromised package | supply chain | High | Low | Third-party packages | ENVIRONMENT | Hash-pinned lockfiles; runtime needs only pyserial + setuptools; CHK-01; DR-01/DR-03 | Low |
| R-011 | Bluetooth drops or COM port held by another device | operational | Medium | Medium | BT SPP on Windows | C-012 | HANDOFF §6 (no other devices); DR-07; USB fallback rank 2 | Medium |
| R-012 | Adapter left plugged in drains the battery | operational | Low | Low | Idle current | C-011 | Checklist step 8: disconnect after session | Low |
| R-013 | Live CSV grows large on long sessions | scale | Low | Low | Unbounded duration | D-017 | `--duration` required default 10 s; user-set | Low |
| R-014 | Passive capture disturbs the bus | security | High | Low | Non-listen-only interface | D-018 | Only slcan listen-only or virtual (T-S11, T-S12); receive-only wrapper; G-004 | Low |
| R-015 | Real adapter text differs from FakeElm | technical | Medium | Medium | Fixture from emulator, not hardware | C-020 | Parser tolerant of CR/LF/trailing spaces; DR-06 TEST_CHALLENGE path | Medium |
| R-016 | A frozen test is unsatisfiable | technical | High | Low | Spec/test mismatch | D-020 | Reference implementation passed 174/174 (spike S7) | Low |
| R-017 | VIN or transcripts committed to the public repo | security | High | Medium | Real-bike outputs | D-008 | Redaction default; `runs/` and outputs git-ignored; CHK-03 | Low |
| R-018 | Bike has a different connector than C-001 | research assumption | High | Low | C-001 single-source | C-001 | G-003 steps 1–2; DR-10 | Low |
| R-019 | Owner expects ABS/suspension codes | scope | Medium | Medium | Generic OBD is engine-only (C-007) | C-007, A-006 | Stated in HARDWARE.md and README; stretch G-004 | Medium |
| R-020 | Reviews not independent (no subagents) | integrity | Medium | Certain | Environment limitation | D-021, A-001 | Role separation, mechanical CHK-04, refimpl satisfiability; human gates | Medium |
| R-021 | Windows-only defects found late | technical | High | Medium | Implementer on Linux (A-013) | A-008, A-013 | Pure-Python deps; encodings/newlines specified (D-016, D-017); G-003 Windows run; T-O02/T-O04 portable | Medium |
| R-022 | Codes cleared through an Android app | operational | Medium | Low | App outside our control | A-015 | README warning; tool itself is read-only | Medium |
| R-023 | OBDLink prices exceed £150 with lead | cost | Low | Medium | Prices not re-verified | A-009 | DR-08 | Low |
| R-024 | Loss of diagnostic evidence if the lead is removed in rain | operational | Low | Low | Exposed connector | D-002 | Sessions on a stand, dry; refit connector cap | Low |
| R-025 | Load-bearing claims C-007, C-019 remain single-source after round 3 | research assumption | Medium | — | No Tier 1 available | C-007, C-019 | Neither changes a frozen test; both handled by gates/ranking | Low |

## v3.9 addendum risk round (2026-11-02)

| Risk | Severity | Mitigation | Status |
|---|---|---|---|
| No independent fresh-context review (D-906) | High | Recorded substitution; independent review scheduled before product execution resumes | Open |
| CI-dependent checks (mutation pricing/floor, matrix jobs) not locally executable (D-905) | Medium | CI is the authoritative venue; estimates labelled; post-conditions gate in CI | Open |
| Lesson/knowledge store push pending G-003 sign-off | Low | Bundle fallback documented; does not block amendment completion | Open |

Pre-mortem rounds repeated to zero Critical risks; the High risk is retained
honestly with owner and mitigation.
