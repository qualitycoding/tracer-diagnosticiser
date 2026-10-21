# Gate G-003 — first on-bike session

Trigger: step S-012. Hardware owned: OBDLink MX+ with moulded ISO 19689 6-pin to 16-pin lead (G-002a proceed). You run this on the Windows laptop and fill in the blanks. Keep `runs\` out of git.

Extra item for this run: in step 5, if `probe` fails at the reset step, note the exact text the adapter prints for `ATZ` (use any serial terminal) and send it back; the transport expects the word ELM327.

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
