from pathlib import Path

from scripts.ba_context import build_context


def seed_project(tmp_path: Path):
    ba = tmp_path / ".ba"
    (ba / "changes").mkdir(parents=True)
    for name in ["PROJECT.md", "REQUIREMENTS.md", "DECISIONS.md", "RESEARCH.md"]:
        (ba / name).write_text(f"# {name}\n", encoding="utf-8")

    def chg(change_id, status):
        final_confirmation = "CONFIRMED" if status == "APPLIED" else "PENDING"
        impact_confirmation = "CONFIRMED" if status == "APPLIED" else "PENDING"
        post = "VERIFIED" if status == "APPLIED" else "PENDING"
        body = "\n## Applied Result\nApplied.\n" if status == "APPLIED" else ""
        (ba / "changes" / f"{change_id}.md").write_text(
            f"""---
contract_version: 0.8
change_id: {change_id}
status: {status}
impact_level: IMPACT_UNKNOWN
impact_confirmation: {impact_confirmation}
final_confirmation: {final_confirmation}
post_commit_verification: {post}
blocking_status: CLEAR
---
# {change_id}
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

    chg("CHG-0001", "REVALIDATING")
    chg("CHG-0002", "APPLIED")
    phases = ba / "phases/02-requirements"
    phases.mkdir(parents=True)
    (phases / "R001.md").write_text("# history\n", encoding="utf-8")


def test_default_context_keeps_open_change_contents_out_of_ambient_context(tmp_path):
    seed_project(tmp_path)
    payload = build_context(tmp_path)
    assert ".ba/PROJECT.md" in payload["current"]
    assert payload["open_changes"] == [".ba/changes/CHG-0001.md"]
    assert payload["selected_changes"] == []
    assert ".ba/changes/CHG-0001.md" not in payload["read_set"]
    assert all("phases/" not in p for p in payload["read_set"])
    assert ".ba/changes/CHG-0002.md" not in payload["read_set"]


def test_identity_review_selects_all_open_changes(tmp_path):
    seed_project(tmp_path)
    payload = build_context(tmp_path, identity_review=True)
    assert payload["selected_changes"] == [".ba/changes/CHG-0001.md"]
    assert payload["focus_status"] == "IDENTITY_REVIEW"


def test_focus_change_selects_only_named_open_change(tmp_path):
    seed_project(tmp_path)
    payload = build_context(tmp_path, "CHG-0001")
    assert payload["selected_changes"] == [".ba/changes/CHG-0001.md"]


def test_applied_change_cannot_be_selected_as_open_focus(tmp_path):
    seed_project(tmp_path)
    payload = build_context(tmp_path, "CHG-0002")
    assert payload["selected_changes"] == []
    assert payload["focus_status"] == "NOT_OPEN"
