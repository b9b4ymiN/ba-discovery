from pathlib import Path

from scripts.ba_lint import lint_project

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/order-allocation-planner"


def test_example_project_lints_cleanly():
    result = lint_project(EXAMPLE)
    assert result.error_count == 0, result.diagnostics


def test_example_snapshots_have_approval_and_handoff():
    snapshots = sorted((EXAMPLE / ".ba/phases").glob("*/*.md"))
    assert len(snapshots) == 4
    for path in snapshots:
        text = path.read_text(encoding="utf-8")
        assert "## Approval" in text
        assert "## Handoff to Next Phase" in text


def test_example_uses_v06_state_contract():
    project = (EXAMPLE / ".ba/PROJECT.md").read_text(encoding="utf-8")
    assert "id_counters" not in project
    assert "current_phase: SPEC" in project
    for legacy in ["BACKGROUND_DISCOVERY", "REQUIREMENT_DISCOVERY", "SYSTEM_DESIGN", "FINAL_FRD"]:
        assert legacy not in project
    for field in ["source:", "provenance:", "validation:"]:
        assert field in project


def test_example_report_keeps_all_fixed_sections():
    report = (EXAMPLE / "docs/BA-FRD-Report.html").read_text(encoding="utf-8")
    assert "BA-ELI5-FRD v1.0" in report
    for i in range(1, 16):
        assert f'data-ba-section="{i}"' in report
    assert "{{" not in report


def test_change_managed_example_keeps_current_truth_clean_and_history_traceable():
    root = ROOT / "examples/change-managed-moq-planner"
    result = lint_project(root)
    assert result.error_count == 0, result.diagnostics

    decisions = (root / ".ba/DECISIONS.md").read_text(encoding="utf-8")
    applied = (root / ".ba/changes/CHG-0001.md").read_text(encoding="utf-8")
    pending = (root / ".ba/changes/CHG-0002.md").read_text(encoding="utf-8")

    assert "MOQ depends on Package Size" in decisions
    assert "MOQ = 5,000" not in decisions
    assert "MOQ = 5,000" in applied
    assert "status: APPLIED" in applied
    assert "post_commit_verification: VERIFIED" in applied
    assert "status: AWAITING_IMPACT_CONFIRMATION" in pending
