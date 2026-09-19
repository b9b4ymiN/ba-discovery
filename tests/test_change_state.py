from pathlib import Path
import pytest

from scripts.change_state import (
    ChangeStateError,
    load_change,
    open_changes,
    rewrite_change_frontmatter,
)


def write_change(root: Path, change_id: str, status: str = "PROPOSED") -> Path:
    changes = root / ".ba/changes"
    changes.mkdir(parents=True, exist_ok=True)
    path = changes / f"{change_id}.md"
    path.write_text(
        f"""---
contract_version: 0.8
change_id: {change_id}
status: {status}
impact_level: IMPACT_UNKNOWN
impact_confirmation: PENDING
final_confirmation: PENDING
post_commit_verification: PENDING
blocking_status: CLEAR
---
# {change_id} — Example

## What is changing?
Before → proposed.

## Why are we changing this?
Business intent changed.

## Change Identity
Business Concern: MOQ

## Impact
Not confirmed.

## Revalidation
Not started.

## Candidate Truth
Not final.

## Final Confirmation
Not confirmed.
""",
        encoding="utf-8",
    )
    return path


def test_load_change_parses_v08_frontmatter(tmp_path):
    path = write_change(tmp_path, "CHG-0001")
    state = load_change(path)
    assert state.change_id == "CHG-0001"
    assert state.status == "PROPOSED"
    assert state.impact_level == "IMPACT_UNKNOWN"


def test_filename_must_match_change_id(tmp_path):
    path = write_change(tmp_path, "CHG-0001")
    wrong = path.with_name("CHG-0002.md")
    path.rename(wrong)
    with pytest.raises(ChangeStateError, match="filename"):
        load_change(wrong)


def test_open_changes_excludes_terminal_states(tmp_path):
    write_change(tmp_path, "CHG-0001", "REVALIDATING")
    write_change(tmp_path, "CHG-0002", "APPLIED")
    assert [c.change_id for c in open_changes(tmp_path / ".ba")] == ["CHG-0001"]


def test_rewrite_change_frontmatter_preserves_body(tmp_path):
    path = write_change(tmp_path, "CHG-0001")
    before = path.read_text(encoding="utf-8")
    rewrite_change_frontmatter(path, status="ANALYZING")
    after = path.read_text(encoding="utf-8")
    assert "status: ANALYZING" in after
    assert before.split("---", 2)[2] == after.split("---", 2)[2]


def test_rewrite_invalid_frontmatter_update_leaves_file_unchanged(tmp_path):
    path = write_change(tmp_path, "CHG-0001")
    before = path.read_bytes()

    with pytest.raises(ChangeStateError, match="invalid change status"):
        rewrite_change_frontmatter(path, status="BOGUS")

    assert path.read_bytes() == before
