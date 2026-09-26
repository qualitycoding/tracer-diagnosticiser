# tracer-diagnosticiser

Read-only on-board diagnostics for a 2022 Yamaha Tracer 9 GT (UK, Euro 5), using the bike's red 6-pin ISO 19689 diagnostic socket, an ISO 19689→OBD-II lead and an OBDLink adapter.

**Status:** planning complete on branch `gen-20260926T164526Z-tracer9gt-obd-reader`; implementation not started. Start with [`HANDOFF.md`](HANDOFF.md). Hardware recommendation: [`plan/HARDWARE.md`](plan/HARDWARE.md).

The tool will never clear codes or write to the bike. Outputs redact the VIN by default.
