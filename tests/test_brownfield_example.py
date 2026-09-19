from pathlib import Path

from scripts.ba_lint import lint_project

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/brownfield-capacity-planner"


def test_brownfield_example_has_existing_system_project_brain_and_report():
    expected = [
        "existing-system/README.md",
        "existing-system/docs/current-workflow.md",
        "existing-system/src/planner.py",
        ".ba/PROJECT.md",
        ".ba/REQUIREMENTS.md",
        ".ba/DECISIONS.md",
        ".ba/RESEARCH.md",
        "docs/BA-FRD-Report.html",
    ]
    for rel in expected:
        assert (EXAMPLE / rel).is_file(), rel


def test_brownfield_example_lints_cleanly():
    result = lint_project(EXAMPLE)
    assert result.error_count == 0, result.diagnostics


def test_brownfield_example_demonstrates_source_gate_and_provenance():
    project = (EXAMPLE / ".ba/PROJECT.md").read_text(encoding="utf-8")
    research = (EXAMPLE / ".ba/RESEARCH.md").read_text(encoding="utf-8")
    workflow = (EXAMPLE / "existing-system/docs/current-workflow.md").read_text(encoding="utf-8")
    combined = project + "\n" + research
    assert "existing-system/docs/current-workflow.md" in combined
    assert "not asked" in combined.lower()
    assert "stakeholder" in combined.lower()
    assert "existing-system constraint" in combined.lower()
    assert "future requirement" in combined.lower()
    assert "source of truth" in workflow.lower()


def test_brownfield_example_has_four_approved_snapshots():
    snapshots = sorted((EXAMPLE / ".ba/phases").glob("*/*.md"))
    assert len(snapshots) == 4
    for path in snapshots:
        text = path.read_text(encoding="utf-8")
        assert "## Approval" in text
        assert "## Handoff to Next Phase" in text
