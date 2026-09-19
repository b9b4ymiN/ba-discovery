import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {
    "ask-ba",
    "ba-discovery",
    "ba-understand",
    "ba-requirements",
    "ba-design",
    "ba-spec",
    "ba-report",
    "ba-change",
}


def test_exact_skill_set_is_preserved():
    found = {p.name for p in (ROOT / "skills").iterdir() if p.is_dir()}
    assert found == EXPECTED_SKILLS


def test_manifest_version_matches_version_file():
    expected = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    assert manifest["version"] == expected


def test_validator_does_not_hardcode_release_version():
    validator = (ROOT / "tests/validate_repo.py").read_text(encoding="utf-8")
    assert 'data["version"] == "0.5.1-rc1"' not in validator


def test_shared_contracts_exist_at_plugin_root():
    expected = {"contract-core.md", "contract-records.md", "contract-snapshots.md"}
    found = {p.name for p in (ROOT / "shared").glob("*.md")} if (ROOT / "shared").exists() else set()
    assert expected <= found


def test_old_nested_project_brain_contract_is_gone():
    assert not (ROOT / "skills/ba-discovery/references/project-brain-contract.md").exists()


def test_phase_skills_reference_plugin_root_shared_contracts():
    phase_skills = ["ba-discovery", "ba-understand", "ba-requirements", "ba-design", "ba-spec"]
    for name in phase_skills:
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert "${CLAUDE_PLUGIN_ROOT}/shared/" in text
        assert "../ba-discovery/references/project-brain-contract.md" not in text


def test_current_state_uses_unified_phase_vocabulary():
    legacy = ["BACKGROUND_DISCOVERY", "REQUIREMENT_DISCOVERY", "SYSTEM_DESIGN", "FINAL_FRD"]
    for name in ["ba-discovery", "ba-understand", "ba-requirements", "ba-design", "ba-spec"]:
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        for token in legacy:
            assert token not in text


def test_shared_contracts_do_not_require_id_counters():
    if not (ROOT / "shared").exists():
        raise AssertionError("shared contracts do not exist")
    combined = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "shared").glob("*.md"))
    assert "id_counters" not in combined


def test_question_contract_has_adaptive_question_classes():
    path = ROOT / "shared/question-contract.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    for phrase in [
        "Decision-critical",
        "Concept calibration",
        "Factual / low-risk",
        "Validation / confirmation",
        "Never outsource expert reasoning",
        "2–4",
        "Explain enough, not a course",
        "uncertain signal",
    ]:
        assert phrase in text


def test_reasoning_phase_skills_reference_question_contract():
    for name in ["ba-understand", "ba-requirements", "ba-design", "ba-spec"]:
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert "${CLAUDE_PLUGIN_ROOT}/shared/question-contract.md" in text
        assert "Prefer one high-value question per turn" not in text
        assert "Ask one high-value question at a time" not in text


def test_question_contract_forbids_percentage_progress():
    text = (ROOT / "shared/question-contract.md").read_text(encoding="utf-8")
    assert "Do not fabricate percentage completion" in text


def test_snapshot_contract_requires_approval_provenance():
    text = (ROOT / "shared/contract-snapshots.md").read_text(encoding="utf-8")
    for phrase in [
        "## Approval",
        "APPROVED_WITH_OPEN_ITEMS",
        "Approved by",
        "Approval scope",
        "Open / excluded from approval",
        "Approval basis",
    ]:
        assert phrase in text


def test_phase_exit_requires_scoped_approval_before_snapshot():
    for name in ["ba-understand", "ba-requirements", "ba-design", "ba-spec"]:
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert "approval scope" in text.lower()
        assert "selective correction" in text.lower()
        assert "## Approval" in text


def test_mutating_skills_integrate_ba_lint_truthfully():
    for name in ["ba-discovery", "ba-understand", "ba-requirements", "ba-design", "ba-spec"]:
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert "${CLAUDE_PLUGIN_ROOT}/scripts/ba_lint.py" in text
        assert "deterministic lint was not run" in text.lower()


def test_ba_spec_blocks_structural_consistency_claim_on_lint_error():
    text = (ROOT / "skills/ba-spec/SKILL.md").read_text(encoding="utf-8")
    assert "lint ERROR" in text
    assert "do not claim final structural consistency" in text


def test_ask_ba_has_exit_routes_and_read_only_frontmatter():
    text = (ROOT / "skills/ask-ba/SKILL.md").read_text(encoding="utf-8")
    frontmatter = text.split("---", 2)[1]
    assert "disallowed-tools:" in frontmatter
    assert "Write" in frontmatter and "Edit" in frontmatter and "Bash" in frontmatter
    assert "Engineering workflow" in text
    assert "No BA needed" in text
    assert "BA capability" in text


def test_ba_report_has_fixed_self_contained_html_shell():
    template = ROOT / "skills/ba-report/assets/report-template.html"
    assert template.exists()
    text = template.read_text(encoding="utf-8")
    for phrase in [
        "<!doctype html>",
        '<meta name="viewport"',
        "@media print",
        "BA-ELI5-FRD v1.0",
        'class="report-meta"',
        'class="summary-box"',
        'class="plain-language"',
        'class="flow"',
        'class="capability"',
        'class="rule-table"',
        'class="traceability"',
        'class="risk"',
        'class="open-item"',
    ]:
        assert phrase in text
    ids = [
        "background", "goal", "what-we-will-do", "scope-boundaries", "current-future",
        "system-logic", "functional-requirements", "business-rules", "data-integrations",
        "roles-permissions", "exceptions-edge-cases", "non-functional-requirements",
        "acceptance-success", "risks-assumptions-open-items", "technical-reference-traceability",
    ]
    for i, section_id in enumerate(ids, start=1):
        assert f'<section id="{section_id}" data-ba-section="{i}">' in text
    lowered = text.lower()
    assert "https://" not in lowered and "http://" not in lowered


def test_ba_report_instructs_fill_not_redesign():
    text = (ROOT / "skills/ba-report/SKILL.md").read_text(encoding="utf-8")
    assert "assets/report-template.html" in text
    assert "do not redesign" in text.lower()


def test_static_validator_covers_v06_assets():
    text = (ROOT / "tests/validate_repo.py").read_text(encoding="utf-8")
    for phrase in ["shared/question-contract.md", "scripts/ba_lint.py", "assets/report-template.html", "examples/order-allocation-planner"]:
        assert phrase in text


def test_readmes_document_v06_question_integrity_and_example():
    en = (ROOT / "README.md").read_text(encoding="utf-8")
    th = (ROOT / "README.th.md").read_text(encoding="utf-8")
    for phrase in ["Question Contract", "Decision-critical", "CANONICAL", "Engineering workflow", "No BA needed", "examples/order-allocation-planner"]:
        assert phrase in en
    for phrase in ["Question Contract", "Decision-critical", "CANONICAL", "Engineering workflow", "No BA needed", "examples/order-allocation-planner"]:
        assert phrase in th


def test_readmes_document_v07_behavioral_eval_and_vendor_neutrality():
    en = (ROOT / "README.md").read_text(encoding="utf-8")
    th = (ROOT / "README.th.md").read_text(encoding="utf-8")
    for phrase in ["Behavioral Confidence", "ba_eval.py", "Brownfield", "vendor-neutral", "No vendor-specific feature is required for BA Discovery correctness."]:
        assert phrase in en
    for phrase in ["Behavioral Confidence", "ba_eval.py", "Brownfield", "vendor-neutral", "No vendor-specific feature is required for BA Discovery correctness."]:
        assert phrase in th


def test_static_validator_covers_v07_eval_assets():
    text = (ROOT / "tests/validate_repo.py").read_text(encoding="utf-8")
    for phrase in [
        "scripts/ba_eval.py",
        "evals/behavior-contract.md",
        "evals/schema/run-record.schema.json",
        "evals/schema/expectations.schema.json",
        "examples/brownfield-capacity-planner",
    ]:
        assert phrase in text


def test_v08_change_contract_exists_and_declares_core_invariants():
    path = ROOT / "shared/contract-changes.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    for phrase in [
        "Single User Only",
        "PROPOSED",
        "ANALYZING",
        "AWAITING_IMPACT_CONFIRMATION",
        "IMPACT_CONFIRMED",
        "REVALIDATING",
        "AWAITING_FINAL_CONFIRMATION",
        "APPLIED",
        "CANCELLED",
        "SUPERSEDED",
        "NON_SEMANTIC",
        "LOCAL",
        "PROPAGATING",
        "FOUNDATIONAL",
        "IMPACT_UNKNOWN",
        "MATCH_EXISTING",
        "NEW_CHANGE",
        "UNCERTAIN",
        "Stage the change, commit the truth.",
        "Preserve confirmed understanding; revalidate only the delta.",
        "Current truth for work. History on demand.",
    ]:
        assert phrase in text


def test_core_contract_treats_open_changes_as_staging_not_truth():
    text = (ROOT / "shared/contract-core.md").read_text(encoding="utf-8")
    assert "OPEN CHANGE" in text
    assert "not canonical truth" in text.lower()
    assert "History on demand" in text


def test_question_contract_is_single_user_not_multi_stakeholder():
    text = (ROOT / "shared/question-contract.md").read_text(encoding="utf-8")
    assert "Single User Only" in text
    assert "another owner" not in text
    assert "stakeholder routing" not in text.lower()


def test_snapshot_contract_uses_current_user_for_new_approvals():
    text = (ROOT / "shared/contract-snapshots.md").read_text(encoding="utf-8")
    assert "**Approved by:** Current user" in text


def test_ba_change_skill_has_vendor_neutral_single_front_door_contract():
    path = ROOT / "skills/ba-change/SKILL.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    frontmatter = text.split("---", 2)[1]
    assert "name: ba-change" in frontmatter
    assert "description: Use when" in frontmatter
    for phrase in [
        "${CLAUDE_PLUGIN_ROOT}/shared/contract-changes.md",
        "${CLAUDE_PLUGIN_ROOT}/scripts/ba_context.py",
        "${CLAUDE_PLUGIN_ROOT}/scripts/ba_lint.py",
        "${CLAUDE_PLUGIN_ROOT}/scripts/ba_change_commit.py",
        "Single Front Door",
        "Read before relating",
        "Focused Evidence Traversal",
        "Minimum Revalidation",
        "Final Before → After",
    ]:
        assert phrase in text


def test_ask_ba_routes_changes_to_ba_change():
    text = (ROOT / "skills/ask-ba/SKILL.md").read_text(encoding="utf-8")
    assert "/ba-change" in text
    assert "approved truth" in text.lower()


def test_reasoning_skills_reference_change_contract():
    for name in ["ba-discovery", "ba-understand", "ba-requirements", "ba-design", "ba-spec"]:
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert "${CLAUDE_PLUGIN_ROOT}/shared/contract-changes.md" in text
        assert "pending" in text.lower()


def test_report_does_not_merge_pending_change_into_approved_truth():
    text = (ROOT / "skills/ba-report/SKILL.md").read_text(encoding="utf-8")
    assert "pending change" in text.lower()
    assert "approved truth" in text.lower()


def test_readmes_document_v08_change_management():
    en = (ROOT / "README.md").read_text(encoding="utf-8")
    th = (ROOT / "README.th.md").read_text(encoding="utf-8")
    for phrase in [
        "/ba-change",
        "Single User Only",
        "Stage the change, commit the truth.",
        "Current truth for work. History on demand.",
        "Pending change",
    ]:
        assert phrase in en
        assert phrase in th


def test_v08_release_version():
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "0.8.0-rc1"


def test_snapshot_contract_uses_user_language_for_approval_basis():
    text = (ROOT / "shared/contract-snapshots.md").read_text(encoding="utf-8")
    assert "**Approval basis:** Explicit user approval in the active BA session." in text
    assert "**Approval basis:** Explicit stakeholder approval in the active BA session." not in text
