# Research round 2 — synthesis, gaps, depth, spikes (R3, R4, R6)

Gap analysis (R3): load-bearing C-005 had only Tier 2/4 support; C-003 lacks Tier 1 pinout; no contradiction found. Version check: python-OBD 0.7.3, python-can 4.6.1, ELM327-emulator 4.0.0 pinned.
Depth (R4) queries: Euro 5 OBD stage II / Reg. 2019/129 (→ C-009, Tier 1); OBDLink EX/MX+ protocol and OS tables (→ C-011, C-012, Tier 1).
Spikes (R6), all committed with outputs in `research/spikes/`:
- S1 `spike_pyobd_emu.py` — python-OBD auto-detects CAN 11/500 against the emulator → C-013 verified.
- S2 `spike_decode_oracle.py` — DTC and PID oracle values → C-014, C-015 verified.
- S3 `spike_can_virtual.py` — python-can virtual bus; slcan listen_only → C-016 verified.
- S4 `spike_bitmap_oracle.py` — supported-PID bitmaps → C-015 verified.
- S5 `spike_emu_raw.py` — raw ELM text format → C-020 verified; FakeElm built from it.
Result: C-005 cannot be raised above `inferred` by any sandbox spike (needs the bike); frozen the procedure instead (DR-05, G-003).
