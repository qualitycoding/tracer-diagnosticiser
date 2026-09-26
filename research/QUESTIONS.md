# Question tree (profile `software` only)

Each leaf names what it informs. Pruned leaves are listed at the end.

## Q1 Physical access
- Q1.1 Which connector does a 2022 Tracer 9 GT use? → C-001, C-002 → D-002, G-003 step 1
- Q1.2 Where is it? → C-023 → G-003 step 1 (owner's manual)
- Q1.3 Which lead converts it to J1962 16-pin, and what pins must carry power/ground? → C-003, C-004 → D-003, G-003 step 3
## Q2 Protocol
- Q2.1 Does the engine ECU answer generic OBD (SAE J1979) through that connector? → C-005 (inferred) → DR-05, R-001
- Q2.2 CAN or K-line; 11 or 29 bit? → C-006, C-005 → D-012 (auto protocol ATSP0; parser handles both header sizes)
- Q2.3 Which modules are reachable (engine vs dash/ABS/IMU/suspension)? → C-007, C-008 → A-006, D-018, G-004
- Q2.4 Which services/monitors are legally required on a 2022 Euro 5 bike? → C-009 → D-014 (discover supported PIDs)
## Q3 Hardware
- Q3.1 Which adapters support the needed protocols on Windows USB/BT and Android BT? → C-011, C-012 → HARDWARE.md, D-001
- Q3.2 Are cheap clones adequate? → C-019 → D-001
- Q3.3 What closed/OEM tools exist and what do they cost? → C-010, C-017, C-018 → HARDWARE.md
- Q3.4 Passive CAN capture hardware for stretch discovery? → C-016 → D-018
## Q4 Software
- Q4.1 Does a Python stack speak ELM327 CAN reliably? → C-013 (spike S1) → D-005
- Q4.2 DTC/PID decoding rules → C-014, C-015 → T-U01..T-U12
- Q4.3 ELM response text format → C-020 → FakeElm, T-U13..T-U20
- Q4.4 Listen-only CAN in python-can → C-016 → T-S12
## Q5 Security / safety
- Q5.1 Can the port be used to write/flash the ECU? → C-022 → D-011 (default-deny), R-003
- Q5.2 Personal data exposure (VIN) → D-016 redaction, .gitignore `runs/`, R-017
- Q5.3 Supply chain → pinned hashed lockfiles, pip-audit (CHK-01)
## Q6 Operations
- Q6.1 Battery drain / low voltage during ignition-on sessions → D-014 LOW_VOLTAGE_THRESHOLD, R-004
- Q6.2 Bluetooth link loss → DR-07

## Pruned (inform nothing in scope)
- ECU flashing/tuning tools (Woolich, IXI, FTECU) — out of scope by A-005 (read-only).
- Dash-menu code retrieval — S11 reports Gen-3 Tracer has none.
