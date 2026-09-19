from pathlib import Path

from scripts.ba_lint import lint_project

ROOT = Path(__file__).resolve().parents[1]


def lint_fixture(name: str):
    return lint_project(ROOT / "tests" / "fixtures" / name)


def test_duplicate_requirement_id_is_error():
    result = lint_fixture("duplicate-id")
    assert any(d.code == "DUPLICATE_ID" and d.severity == "ERROR" for d in result.diagnostics)


def test_id_gap_is_not_an_error():
    result = lint_fixture("valid-project")
    assert not any(d.code == "ID_GAP" for d in result.diagnostics)


def test_dangling_reference_is_error():
    result = lint_fixture("dangling-reference")
    assert any(d.code == "DANGLING_REFERENCE" and d.severity == "ERROR" for d in result.diagnostics)


def test_invalid_phase_and_lifecycle_are_errors():
    result = lint_fixture("invalid-state")
    codes = {d.code for d in result.diagnostics if d.severity == "ERROR"}
    assert "INVALID_PHASE_VALUE" in codes
    assert "INVALID_LIFECYCLE_VALUE" in codes


def test_legacy_phase_is_warning_not_error():
    result = lint_fixture("legacy-v051")
    assert any(d.code == "LEGACY_PHASE_VALUE" and d.severity == "WARNING" for d in result.diagnostics)
    assert not any(d.code == "INVALID_PHASE_VALUE" for d in result.diagnostics)


def test_missing_current_baseline_is_error():
    result = lint_fixture("missing-baseline")
    assert any(d.code == "MISSING_BASELINE" and d.severity == "ERROR" for d in result.diagnostics)


def test_malformed_snapshot_filename_is_error():
    result = lint_fixture("invalid-state")
    assert any(d.code == "INVALID_SNAPSHOT_NAME" and d.severity == "ERROR" for d in result.diagnostics)


def test_v06_snapshot_requires_approval_block():
    path = ROOT / "tests/fixtures/invalid-state/.ba/phases/02-requirements/R001.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\ncontract_version: 0.6\n---\n# Snapshot without approval\n", encoding="utf-8")
    try:
        result = lint_fixture("invalid-state")
        assert any(d.code == "MISSING_APPROVAL_BLOCK" and d.severity == "ERROR" for d in result.diagnostics)
    finally:
        path.unlink()


def test_legacy_snapshot_without_approval_is_not_error():
    result = lint_fixture("legacy-v051")
    assert not any(d.code == "MISSING_APPROVAL_BLOCK" for d in result.diagnostics)


def test_missing_bypass_provenance_is_error():
    result = lint_fixture("bypass-missing-provenance")
    assert any(d.code == "MISSING_BYPASS_PROVENANCE" and d.severity == "ERROR" for d in result.diagnostics)


def test_valid_project_has_zero_errors():
    result = lint_fixture("valid-project")
    assert result.error_count == 0


def test_cli_valid_project_exits_zero_and_prints_summary():
    import subprocess, sys
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/ba_lint.py"), "--project", str(ROOT / "tests/fixtures/valid-project")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "0 error" in proc.stdout


def test_cli_duplicate_project_exits_one():
    import subprocess, sys
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/ba_lint.py"), "--project", str(ROOT / "tests/fixtures/duplicate-id")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
    assert "DUPLICATE_ID" in proc.stdout


def _write_minimal_project(tmp_path):
    ba = tmp_path / ".ba"
    ba.mkdir()
    (ba / "PROJECT.md").write_text("# Project\n", encoding="utf-8")
    (ba / "REQUIREMENTS.md").write_text("", encoding="utf-8")
    (ba / "DECISIONS.md").write_text("", encoding="utf-8")
    return ba


def _write_change(ba, *, status, impact="IMPACT_UNKNOWN",
                  impact_confirmation="PENDING",
                  final_confirmation="PENDING",
                  post_commit="PENDING",
                  blocking="CLEAR"):
    changes = ba / "changes"
    changes.mkdir(exist_ok=True)
    body = "\n## Applied Result\nApplied.\n" if status == "APPLIED" else ""
    (changes / "CHG-0001.md").write_text(
        f"""---
contract_version: 0.8
change_id: CHG-0001
status: {status}
impact_level: {impact}
impact_confirmation: {impact_confirmation}
final_confirmation: {final_confirmation}
post_commit_verification: {post_commit}
blocking_status: {blocking}
---
# CHG-0001 — Example
## What is changing?
x
## Why are we changing this?
x
## Change Identity
x
## Impact
x
## Revalidation
x
## Candidate Truth
x
## Final Confirmation
x
{body}
""",
        encoding="utf-8",
    )


def test_applied_change_requires_full_confirmation_and_readback(tmp_path):
    ba = _write_minimal_project(tmp_path)
    _write_change(ba, status="APPLIED")
    result = lint_project(tmp_path)
    codes = {d.code for d in result.diagnostics}
    assert "INVALID_APPLIED_CHANGE_STATE" in codes


def test_canonical_superseded_record_is_error_in_v08(tmp_path):
    ba = _write_minimal_project(tmp_path)
    (ba / "REQUIREMENTS.md").write_text(
        """## REQ-0001 — Old
```yaml ba-record
id: REQ-0001
kind: REQUIREMENT
status: SUPERSEDED
derived_from: []
evidence: []
related: []
superseded_by: null
```
""",
        encoding="utf-8",
    )
    result = lint_project(tmp_path)
    assert any(d.code == "OBSOLETE_RECORD_IN_CANONICAL" for d in result.diagnostics)


def test_canonical_change_provenance_must_resolve(tmp_path):
    ba = _write_minimal_project(tmp_path)
    (ba / "DECISIONS.md").write_text(
        """## DEC-0002 — Current
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
    result = lint_project(tmp_path)
    assert any(d.code == "DANGLING_CHANGE_REFERENCE" for d in result.diagnostics)


def test_malformed_change_does_not_hide_valid_sibling_change_from_provenance(tmp_path):
    ba = _write_minimal_project(tmp_path)
    changes = ba / "changes"
    changes.mkdir(exist_ok=True)

    (changes / "CHG-0001.md").write_text(
        """---
contract_version: 0.8
change_id: CHG-0001
status: BOGUS
impact_level: IMPACT_UNKNOWN
impact_confirmation: PENDING
final_confirmation: PENDING
post_commit_verification: PENDING
blocking_status: CLEAR
---
# CHG-0001 — malformed
""",
        encoding="utf-8",
    )
    (changes / "CHG-0002.md").write_text(
        """---
contract_version: 0.8
change_id: CHG-0002
status: REVALIDATING
impact_level: LOCAL
impact_confirmation: CONFIRMED
final_confirmation: PENDING
post_commit_verification: PENDING
blocking_status: CLEAR
---
# CHG-0002 — valid
## What is changing?
x
## Why are we changing this?
x
## Change Identity
x
## Impact
x
## Revalidation
x
## Candidate Truth
x
## Final Confirmation
x
""",
        encoding="utf-8",
    )
    (ba / "DECISIONS.md").write_text(
        """## DEC-0002 — Current
```yaml ba-record
id: DEC-0002
kind: DECISION
status: CONFIRMED
derived_from: [CHG-0002]
evidence: []
related: []
superseded_by: null
```
""",
        encoding="utf-8",
    )

    result = lint_project(tmp_path)
    invalid_change_diags = [d for d in result.diagnostics if d.code == "INVALID_CHANGE_RECORD"]

    assert len(invalid_change_diags) == 1
    assert invalid_change_diags[0].path == ".ba/changes/CHG-0001.md"
    assert not any(d.code == "DANGLING_CHANGE_REFERENCE" and "CHG-0002" in d.message for d in result.diagnostics)
