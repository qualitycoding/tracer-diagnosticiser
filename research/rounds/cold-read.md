# Cold-read gate (Phase 3.6)

Substitution: no fresh subagents (D-021). Each pass was performed by the planning agent in a dry-run role reading only branch contents, followed by the mechanical checker `research/spikes/consistency_check.py` (Haiku role).

## Pass 1 — items found
1. S-006/S-007 pytest selectors mixed file paths with `-k`, which would deselect T-O06/T-S10/T-O08 → rewritten as single `-k` expressions.
2. `dtc` and `info` console output unspecified → specified in D-017 and frozen as T-I10.
3. `live` with an unknown or non-hex PID: exit code unspecified → D-017 (exit 2) and T-O10.
4. Windows COM-port lookup path unverified → marked unverified with Device Manager fallback (ENVIRONMENT.md).
5. CSV/JSON encodings and newlines on Windows unspecified → D-016/D-017 (also pre-mortem R-021).
6. S-001 `git checkout` used a local branch name that a fresh clone does not have → `git fetch` + `origin/` form.
7. Implementer credentials undocumented → HANDOFF §10.
8. Checker: `plan/OPERATIONS.md` (N/A) flagged as a missing referenced path → checker treats it as N/A.
All resolved by amending the plan.

## Pass 2 — items found
None. `consistency_check.py` → CONSISTENT (output below, appended at freeze time).
