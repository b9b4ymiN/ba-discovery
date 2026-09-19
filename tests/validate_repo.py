from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = [
    "ask-ba",
    "ba-discovery",
    "ba-understand",
    "ba-requirements",
    "ba-design",
    "ba-spec",
    "ba-report",
    "ba-change",
]

manifest = ROOT / ".claude-plugin" / "plugin.json"
assert manifest.is_file(), "missing .claude-plugin/plugin.json"
data = json.loads(manifest.read_text(encoding="utf-8"))
assert data["name"] == "ba-discovery"
version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
assert data["version"] == version, (data["version"], version)


readme_en = ROOT / "README.md"
readme_th = ROOT / "README.th.md"
assert readme_en.is_file(), "missing README.md"
assert readme_th.is_file(), "missing README.th.md"

en = readme_en.read_text(encoding="utf-8")
th = readme_th.read_text(encoding="utf-8")
assert "[English](README.md)" in en and "[ไทย](README.th.md)" in en, "missing language switch in README.md"
assert "[English](README.md)" in th and "[ไทย](README.th.md)" in th, "missing language switch in README.th.md"
assert "DreambigOu/ELI5" in en, "English README must recommend ELI5 as an optional companion"
assert "DreambigOu/ELI5" in th, "Thai README must recommend ELI5 as an optional companion"
assert "not required" in en.lower() or "optional" in en.lower(), "English README must keep ELI5 optional"
assert "ไม่จำเป็น" in th or "ทางเลือก" in th, "Thai README must keep ELI5 optional"


# v0.8 shared/runtime/eval assets
for rel in [
    "shared/contract-core.md",
    "shared/contract-records.md",
    "shared/contract-snapshots.md",
    "shared/question-contract.md",
    "scripts/ba_lint.py",
    "skills/ba-report/assets/report-template.html",
    "examples/order-allocation-planner/.ba/PROJECT.md",
    "examples/order-allocation-planner/docs/BA-FRD-Report.html",
    "scripts/ba_eval.py",
    "evals/behavior-contract.md",
    "evals/schema/run-record.schema.json",
    "evals/schema/expectations.schema.json",
    "examples/brownfield-capacity-planner/.ba/PROJECT.md",
    "examples/brownfield-capacity-planner/docs/BA-FRD-Report.html",
    "shared/contract-changes.md",
    "scripts/change_state.py",
    "scripts/ba_context.py",
    "scripts/ba_change_commit.py",
    "skills/ba-change/SKILL.md",
    "examples/change-managed-moq-planner/.ba/PROJECT.md",
    "examples/change-managed-moq-planner/.ba/changes/CHG-0001.md",
]:
    assert (ROOT / rel).exists(), f"missing {rel}"

skills_root = ROOT / "skills"
found = sorted(p.name for p in skills_root.iterdir() if p.is_dir())
assert found == sorted(SKILLS), f"unexpected skills: {found}"

for name in SKILLS:
    skill = skills_root / name / "SKILL.md"
    assert skill.is_file(), f"missing {skill}"
    text = skill.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"missing frontmatter in {name}"
    frontmatter = text.split("---", 2)[1]
    assert re.search(r"(?m)^name:\s*\S+", frontmatter), f"missing name in {name}"
    assert re.search(r"(?m)^description:\s*Use when", frontmatter), f"description must start with 'Use when' in {name}"

report_pattern = skills_root / "ba-report" / "references" / "report-pattern.md"
assert report_pattern.is_file(), "missing report pattern"
report = report_pattern.read_text(encoding="utf-8")
headings = [
    "Background",
    "Goal",
    "What We Will Do",
    "Scope & Boundaries",
    "Current → Future",
    "Project / System Logic",
    "Functional Requirements",
    "Business Rules & Decision Logic",
    "Data & Integrations",
    "Roles, Responsibilities & Permissions",
    "Exceptions & Edge Cases",
    "Non-Functional Requirements",
    "Acceptance & Success Criteria",
    "Risks, Assumptions & Open Items",
    "Technical Reference & Traceability",
]
pos = -1
for heading in headings:
    new_pos = report.find(heading, pos + 1)
    assert new_pos > pos, f"report heading missing/out of order: {heading}"
    pos = new_pos

print(f"PASS: plugin manifest + {len(SKILLS)} skills + v0.8 shared/lint/eval/report/example contracts")
