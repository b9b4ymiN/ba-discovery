"""Phase 02 harness: deterministic structural checks, not semantic AI evaluation."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ba_visual_v2", ROOT / "scripts" / "ba_visual.py")
visual = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visual)


def item(**overrides):
    result = {"visual_id": "workflow", "title": "Workflow", "question": "How does it work?",
              "intent": "process", "kind": "flowchart", "selection_reason": "Ordered actions",
              "level": "L1", "status": "PROPOSED", "source": "flowchart LR\nA --> B",
              "references": [], "source_paths": []}
    result.update(overrides)
    return result


def payload(*items, **overrides):
    result = {"schema_version": 2, "title": "Review", "phase": "REQUIREMENTS",
              "focus_id": items[0]["visual_id"], "visuals": list(items)}
    result.update(overrides)
    return result


@pytest.mark.parametrize("wrong", [
    {"kind": "sequence"},
    {"source": "sequenceDiagram\nA->>B: send"},
    {"level": "L3"},
    {"status": "CONFIRMED"},
    {"status": "OBSERVED"},
    {"status": "APPROVED"},
    {"status": "ASSUMPTION", "references": ["CHG-001"]},
    {"intent": "explain", "kind": "text"},
    {"intent": "screen", "kind": "wireframe"},
])
def test_reject_wrong_contract(tmp_path, wrong):
    with pytest.raises(ValueError):
        visual.normalize_v2(tmp_path, payload(item(**wrong)))


def test_table_and_focused_update(tmp_path):
    src = tmp_path / "workflow.md"
    src.write_text("first")
    first = item(status="OBSERVED", references=["workflow.md"], source_paths=["workflow.md"])
    old = visual.normalize_v2(tmp_path, payload(first))
    src.write_text("changed")
    table = item(visual_id="rules", intent="condition", kind="decision_table",
                 columns=["Condition", "Outcome"], rows=[["Missing", "Open question"]])
    updated = visual.normalize_v2(tmp_path, payload(table), old)
    assert updated["status"] == "DRAFT"
    assert updated["focus_id"] == "rules"
    prior, current = updated["diagrams"]
    assert prior["stale"] and prior["retained"]
    assert prior["sources"] == old["diagrams"][0]["sources"]
    assert current["tab"] == "Rules"
    assert current["rows"] == [["Missing", "Open question"]]
    removed = visual.normalize_v2(tmp_path, payload(table, remove_ids=["workflow"]), updated)
    assert [d["visual_id"] for d in removed["diagrams"]] == ["rules"]


def test_table_shape_and_duplicate_ids(tmp_path):
    with pytest.raises(ValueError):
        visual.normalize_v2(tmp_path, payload(item(), item()))
    with pytest.raises(ValueError):
        visual.normalize_v2(tmp_path, payload(item(intent="condition", kind="decision_table",
                                                 columns=["Condition", "Outcome"], rows=[["Only one"]])))


@pytest.mark.parametrize("path", ["../secret", ".env", ".ba//changes/CHG-001.md", "docs/../file.md", "key.pem"])
def test_excluded_source_paths(tmp_path, path):
    with pytest.raises(ValueError):
        visual.evidence_path(tmp_path, path)


def test_approved_view_requires_current_baseline(tmp_path):
    brain = tmp_path / ".ba"
    folder = brain / "phases" / "02-requirements"
    folder.mkdir(parents=True)
    rel = ".ba/phases/02-requirements/R001.md"
    (tmp_path / rel).write_text("## Approval\n**Status:** APPROVED\nApproval scope: process")
    (brain / "PROJECT.md").write_text("## Current Baselines\n- Requirements: .ba/phases/02-requirements/R002.md\n")
    approved = item(status="APPROVED", references=["REQ-001"], source_paths=[rel, ".ba/PROJECT.md"])
    with pytest.raises(ValueError):
        visual.normalize_v2(tmp_path, payload(approved))
    (brain / "PROJECT.md").write_text("## Current Baselines\n- Requirements: " + rel + "\n")
    result = visual.normalize_v2(tmp_path, payload(approved))
    assert result["diagrams"][0]["status"] == "APPROVED"
    assert result["status"] == "DRAFT"
