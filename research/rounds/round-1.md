# Research round 1 — decompose + breadth (R1, R2)

Tier substitution: no subagents in this environment (D-021); all passes run by the planning agent (Fable/Mythos-class orchestrator acting in each role sequentially), logged in `.checkpoints/state.json`.

Queries (web_search / web_search_fast, 2026-09-26): Tracer 9 GT diagnostic connector 4 pin CAN; HealTech OBD Tool Yamaha Tracer 9 GT; Euro 5 6-pin red connector pinout ISO 19689; MotoScan Yamaha Euro 5 MT-09; Woolich Tracer 9 GT interface; 2021 MT-09 ELM327 ISO 15765-4 CAN 500; Tracer 9 GT OBD ELM327 OBDLink red 6 pin; ISO 19689 pinout JST MWT; Yamaha YDT communication unit Euro 5; Duonix Yamaha supported models.

Findings → C-001..C-004, C-006, C-007, C-010, C-017, C-018 (see `research/claims.json`).
Key result: 2021+ Tracer uses the red ISO 19689 6-pin port, not the older 4-pin. Pinout of the bike-side connector not obtainable from a Tier 1 source (standard paywalled; fz09 thread returned HTTP 402).
New questions: does the engine ECU answer generic OBD (Q2.1)? Which Euro 5 OBD stage applies (Q2.4)?
