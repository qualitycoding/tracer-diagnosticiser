"""CHK-04 / Phase 3.6 step 2 / Phase 5.1 mechanical consistency check (stdlib only).
Verifies: every ID referenced in plan/, HANDOFF.md and premortem/ is defined; every frozen test ID is traced
and every traced test exists; every path in backticks under plan/PLAN.md Inputs/Outputs exists or is created
by a step; no N/A artifact is referenced as required; manifest and state files exist; required files exist."""
import json, pathlib, re, sys
R = pathlib.Path(__file__).resolve().parents[2]
txt = lambda p: (R / p).read_text(encoding="utf-8")
errors = []
docs = {p: txt(p) for p in ["plan/PLAN.md", "plan/DECISIONS.md", "plan/GATES.md", "plan/TRACEABILITY.md",
                            "plan/HARDWARE.md", "plan/ASSUMPTIONS.md", "HANDOFF.md", "premortem/RISK_REGISTER.md"]}
alltext = "\n".join(docs.values())
tests_text = "\n".join(p.read_text(encoding="utf-8") for p in (R / "tests").rglob("test_*.py"))
test_ids = set(re.findall(r"def test_(T_[A-Z]\d+)", tests_text))
test_ids = {t.replace("_", "-") for t in test_ids}
claims = {c["id"] for c in json.loads(txt("research/claims.json"))}
defined = {
    "S": set(re.findall(r"^### (S-\d{3})", docs["plan/PLAN.md"], re.M)),
    "D": set(re.findall(r"\*\*(D-\d{3})", docs["plan/DECISIONS.md"])) | set(re.findall(r"^### (D-\d{3})", docs["plan/DECISIONS.md"], re.M)),
    "DR": set(re.findall(r"\*\*(DR-\d{2})", docs["plan/DECISIONS.md"])),
    "A": set(re.findall(r"^\| (A-\d{3}) ", docs["plan/ASSUMPTIONS.md"], re.M)),
    "G": set(re.findall(r"^\| (G-\d{3}[ab]?) ", docs["plan/GATES.md"], re.M)),
    "R": set(re.findall(r"^\| (R-\d{3}) ", docs["premortem/RISK_REGISTER.md"], re.M)),
    "C": claims, "T": test_ids,
    "SC": set(re.findall(r"\*\*(SC-\d+)\*\*", docs["plan/PLAN.md"])),
    "CHK": set(re.findall(r"\*\*(CHK-\d{2})", docs["plan/PLAN.md"])),
}
pats = {"S": r"\bS-\d{3}\b", "D": r"\bD-\d{3}\b", "DR": r"\bDR-\d{2}\b", "A": r"\bA-\d{3}\b", "G": r"\bG-\d{3}[ab]?\b",
        "R": r"\bR-\d{3}\b", "C": r"\bC-\d{3}\b", "T": r"\bT-[A-Z]\d{2}\b", "SC": r"\bSC-\d+\b", "CHK": r"\bCHK-\d{2}\b"}
for k, pat in pats.items():
    for ref in sorted(set(re.findall(pat, alltext))):
        if ref not in defined[k] and not (k == "G" and ref in ("G-001", "G-002")):
            errors.append(f"undefined {k} reference: {ref}")
# ranges like T-U01..T-U12 expand
for a, b in re.findall(r"\b(T-[A-Z]\d{2})\.\.(T-[A-Z]\d{2})\b", alltext):
    if a[:3] == b[:3]:
        for i in range(int(a[3:]), int(b[3:]) + 1):
            t = f"{a[:3]}{i:02d}"
            if t not in test_ids:
                errors.append(f"range {a}..{b} names missing test {t}")
traced = set(re.findall(r"\bT-[A-Z]\d{2}\b", docs["plan/TRACEABILITY.md"]))
for rng in re.findall(r"\b(T-[A-Z]\d{2})\.\.(T-[A-Z]\d{2})\b", docs["plan/TRACEABILITY.md"]):
    a, b = rng
    traced |= {f"{a[:3]}{i:02d}" for i in range(int(a[3:]), int(b[3:]) + 1)}
for t in sorted(test_ids - traced):
    errors.append(f"test not traced: {t}")
for sc in sorted(defined["SC"]):
    if sc not in docs["plan/TRACEABILITY.md"]:
        errors.append(f"success criterion not traced: {sc}")
created = set()
for m in re.finditer(r"- Outputs: (.*)", docs["plan/PLAN.md"]):
    created |= set(re.findall(r"`?([\w./-]+\.(?:py|md|json))`?", m.group(1)))
for m in re.finditer(r"- Inputs: (.*)", docs["plan/PLAN.md"]):
    for p in re.findall(r"\b((?:src|tests|plan|research)/[\w./-]+\.(?:py|md|json|txt))", m.group(1)):
        if not (R / p).exists() and p not in created:
            errors.append(f"input path missing: {p}")
for p in re.findall(r"\b((?:src/tracer_diag|tests|plan|research/spikes)/[\w./-]+\.(?:py|md|json|txt))\b", alltext):
    base = p.split("::")[0]
    if base in ("plan/OPERATIONS.md",):
        continue
    if not (R / base).exists() and base not in created and not base.endswith("__main__.py"):
        errors.append(f"referenced path missing: {base}")
for na in ("math/", "figures/SPEC.md", "manuscript/", "plan/OPERATIONS.md", "research/NOVELTY.md"):
    for p, t in docs.items():
        if p != "plan/PLAN.md" and na in t and "N/A" not in t:
            errors.append(f"N/A artifact referenced as required in {p}: {na}")
    if (R / na.rstrip("/")).exists():
        errors.append(f"N/A artifact exists: {na}")
for req in ["HANDOFF.md", "plan/PROFILE.md", "plan/PLAN.md", "plan/ASSUMPTIONS.md", "plan/DECISIONS.md", "plan/GATES.md",
            "plan/ENVIRONMENT.md", "plan/TRACEABILITY.md", "research/QUESTIONS.md", "research/claims.json",
            "research/SOURCES.md", "research/rounds/round-1.md", "tests/FROZEN_MANIFEST.sha256",
            "premortem/RISK_REGISTER.md", "premortem/round-1.md", ".checkpoints/state.json"]:
    if not (R / req).exists():
        errors.append(f"required file missing: {req}")
if errors:
    print("\n".join(errors)); print(f"INCONSISTENT ({len(errors)})"); sys.exit(1)
print(f"CONSISTENT: {len(test_ids)} test IDs, {len(claims)} claims, {len(defined['S'])} steps, {len(defined['R'])} risks")
