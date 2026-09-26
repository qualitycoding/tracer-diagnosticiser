# Hardware: requirements and ranked options (v2, re-scored for A-008 platforms)

## What any working setup needs
1. **Bike-side connection:** the red 6-pin Euro 5 diagnostic socket on the 2022 Tracer 9 GT (C-001), standardised as ISO 19689 / JST MWT (C-002). Location: see the owner's manual section "Diagnostic connector" (C-023).
2. **Adapter lead:** a moulded ISO 19689 6-pin (male) → SAE J1962 16-pin (female) lead that wires CAN and K-line (C-003). Not the Yamaha 3-pin or 4-pin leads sold for pre-2021 bikes. Typical price EUR 9–30 (S31, S32).
3. **Interface:** an ELM327-command-set adapter with genuine ISO 15765-4 (CAN) and ISO 14230-4 (K-line) support (C-011), or a raw CAN interface for passive capture only (stretch).
4. **Host:** Windows 10/11 laptop with Python 3.12 (own software), or an Android phone with an ELM327 app (A-008).
5. **Power discipline:** healthy battery; ignition ON, engine OFF, sessions under ~15 min or a battery maintainer (R-004).

## Gate (A-010): credible support for a 2022 Tracer 9 GT engine ECU
Nothing in scope has Tier 1 proof of Tracer-specific support (C-005 is `inferred`). "Pass" below means: vendor/owner reports for 2021+ CP3 Yamahas over the red 6-pin port **and** the protocols required. Final proof is the on-bike probe at G-003.

## Scores (1–5; weights A-010: openness 0.30, cost 0.20, depth 0.20, platform 0.15, safety/support 0.15)

| Rank | Option | Gate | Open | Cost | Depth | Platform | Safety | **Weighted** | Approx. total |
|---|---|---|---|---|---|---|---|---|---|
| **1** | **OBDLink MX+ (Bluetooth) + ISO 19689 lead** | pass | 5 | 3 | 3.5 | 5 | 4 | **4.15** | ~£110–145 |
| 2 | OBDLink EX (USB) + ISO 19689 lead | pass | 5 | 4 | 3.5 | 3 | 5 | **4.20** | ~£75–95 |
| 3 | Generic ELM327 v1.5 Bluetooth + ISO 19689 lead (or a pre-made kit, S16) | pass (weak) | 4 | 5 | 2.5 | 4 | 2 | **3.60** | ~£15–40 |
| 4 | USB-CAN adapter (CANable-class, slcan firmware) + lead — stretch only | conditional (CAN only) | 5 | 4 | 2 | 2 | 3 | **3.45** | ~£30–50 |
| 5 | Stand-alone handheld OBD2 code reader + lead | pass (weak) | 1 | 5 | 2 | 1 | 4 | **2.45** | ~£25–50 |
| 6 | Duonix Bike-Scan 2 Pro, Yamaha ISO 19689 kit | conditional (lists MT-09 / Tracer 900, not Tracer 9 GT; C-017) | 1 | 1 | 5 | 2 | 4 | **2.40** | ~EUR 449 |
| — | Yamaha YDT + 6-pin sub-harness 90890-03266-00 | dealer tool (C-010) | — | — | — | — | — | not scored | dealer visit |
| — | HealTech OBD Tool | excluded: no Yamaha software (C-018) | — | — | — | — | — | — | — |
| — | Tuning/flashing interfaces (Woolich, IXI, FTECU) | excluded by A-005 (read-only); they write to the ECU (C-022) | — | — | — | — | — | — | — |

**Why MX+ is ranked first despite 0.05 fewer points:** ties within 0.10 are broken by coverage of the platforms you named (D-007). MX+ works with both the Windows laptop (Bluetooth SPP → COM port, C-012) and Android apps; EX is USB-only and does not serve the phone. If you decide Windows-only, or MX+ plus lead exceeds £150 at purchase time, choose rank 2 (DR-08).

### Scoring notes
- **Openness:** OBDLink devices speak the documented ELM327 + ST command sets over a serial port (C-011); raw CAN adapters are fully open; handhelds and Duonix are closed.
- **Cost:** OBDLink prices are approximate from the owner's earlier Renault plan, not re-verified here — confirm at G-002. Lead and kit prices from S16, S31, S32; Duonix from S19.
- **Depth:** generic OBD reaches the engine ECU only (C-007); STN adapters add ST commands useful later; Duonix claims multi-module Yamaha coverage.
- **Platform:** A-008 (Windows + Android Bluetooth).
- **Safety/support:** OBDLink: 3-year warranty, secure pairing button (S07); clones: unreliable (C-019), Bluetooth PINs guessable; raw CAN: DIY risk mitigated by listen-only (D-018).

## Recommended purchase (pending G-002)
1. OBDLink MX+.
2. A moulded ISO 19689 6-pin → 16-pin lead from a seller that names "Euro 5 / ISO 19689 / red 6-pin" and "CAN + K-line".
Total within £150 is expected but must be checked at purchase (DR-08).
Optional, stretch only after G-004: a CANable-class USB-CAN adapter with slcan firmware.

## Not needed
Yamaha 3-pin/4-pin leads; splitters (C-021); any "MIL eliminator" device (it clears codes; violates A-005).
