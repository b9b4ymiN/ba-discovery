from pathlib import Path
import pytest

import scripts.ba_change_commit as commit_module
from scripts.ba_change_commit import ChangeCommitError, apply_candidate
from scripts.change_state import load_change


def seed_commit_case(tmp_path: Path, final_confirmation: str):
    project = tmp_path / "project"
    ba = project / ".ba"
    changes = ba / "changes"
    candidate = changes / ".candidate" / "CHG-0001"
    candidate.mkdir(parents=True)
    changes.mkdir(parents=True, exist_ok=True)

    (ba / "PROJECT.md").write_text("# Project\n", encoding="utf-8")
    (ba / "REQUIREMENTS.md").write_text("", encoding="utf-8")
    (ba / "RESEARCH.md").write_text("# Research\n", encoding="utf-8")
    (ba / "DECISIONS.md").write_text(
        """## DEC-0001 — MOQ fixed
```yaml ba-record
id: DEC-0001
kind: DECISION
status: CONFIRMED
derived_from: []
evidence: []
related: []
superseded_by: null
```
### Decision
MOQ = 5,000
""",
        encoding="utf-8",
    )

    (changes / "CHG-0001.md").write_text(
        f"""---
contract_version: 0.8
change_id: CHG-0001
status: AWAITING_FINAL_CONFIRMATION
impact_level: PROPAGATING
impact_confirmation: CONFIRMED
final_confirmation: {final_confirmation}
post_commit_verification: PENDING
blocking_status: CLEAR
---
# CHG-0001 — Change MOQ

## What is changing?
Before: MOQ = 5,000
After: MOQ depends on Package Size

## Why are we changing this?
The rule varies by Package Size.

## Change Identity
Business Concern: MOQ

## Impact
Confirmed.

## Revalidation
Complete.

## Candidate Truth
MOQ depends on Package Size.

## Final Confirmation
{final_confirmation}
""",
        encoding="utf-8",
    )

    (candidate / "DECISIONS.md").write_text(
        """## DEC-0002 — MOQ depends on Package Size
```yaml ba-record
id: DEC-0002
kind: DECISION
status: CONFIRMED
derived_from: [CHG-0001]
evidence: []
related: []
superseded_by: null
```
### Decision
MOQ depends on Package Size.
""",
        encoding="utf-8",
    )
    return project, candidate


def test_rejects_commit_without_final_confirmation(tmp_path):
    project, candidate = seed_commit_case(tmp_path, final_confirmation="PENDING")
    before = (project / ".ba/DECISIONS.md").read_bytes()
    with pytest.raises(ChangeCommitError, match="final confirmation"):
        apply_candidate(project, "CHG-0001", candidate)
    assert (project / ".ba/DECISIONS.md").read_bytes() == before


def test_lint_failure_leaves_canonical_unchanged(tmp_path):
    project, candidate = seed_commit_case(tmp_path, final_confirmation="CONFIRMED")
    (candidate / "DECISIONS.md").write_text(
        """## DEC-0002 — bad
```yaml ba-record
id: DEC-0002
kind: DECISION
status: CONFIRMED
derived_from: [CHG-9999]
evidence: []
related: []
superseded_by: null
```
""",
        encoding="utf-8",
    )
    before = (project / ".ba/DECISIONS.md").read_bytes()
    with pytest.raises(ChangeCommitError, match="prospective state"):
        apply_candidate(project, "CHG-0001", candidate)
    assert (project / ".ba/DECISIONS.md").read_bytes() == before


def test_successful_commit_reads_back_and_marks_applied(tmp_path):
    project, candidate = seed_commit_case(tmp_path, final_confirmation="CONFIRMED")
    candidate_bytes = (candidate / "DECISIONS.md").read_bytes()
    touched = apply_candidate(project, "CHG-0001", candidate)
    assert ".ba/DECISIONS.md" in touched
    assert (project / ".ba/DECISIONS.md").read_bytes() == candidate_bytes
    state = load_change(project / ".ba/changes/CHG-0001.md")
    assert state.status == "APPLIED"
    assert state.post_commit_verification == "VERIFIED"
    assert "## Applied Result" in (project / ".ba/changes/CHG-0001.md").read_text(encoding="utf-8")
    assert not candidate.exists()


def test_mid_commit_failure_rolls_back_all_files(tmp_path, monkeypatch):
    project, candidate = seed_commit_case(tmp_path, final_confirmation="CONFIRMED")
    (candidate / "PROJECT.md").write_text("# Project changed\n", encoding="utf-8")
    original_project = (project / ".ba/PROJECT.md").read_bytes()
    original_decisions = (project / ".ba/DECISIONS.md").read_bytes()

    calls = {"n": 0}
    real_replace = commit_module._replace_bytes

    def fail_second(path, payload):
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError("simulated write failure")
        return real_replace(path, payload)

    monkeypatch.setattr(commit_module, "_replace_bytes", fail_second)
    with pytest.raises(ChangeCommitError, match="rolled back"):
        apply_candidate(project, "CHG-0001", candidate)

    assert (project / ".ba/PROJECT.md").read_bytes() == original_project
    assert (project / ".ba/DECISIONS.md").read_bytes() == original_decisions
