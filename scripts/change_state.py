from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

CHANGE_ID_RE = re.compile(r"^CHG-[0-9]{4,}$")
CHANGE_FILE_RE = re.compile(r"^CHG-[0-9]{4,}\.md$")

ALL_STATUSES = {
    "PROPOSED",
    "ANALYZING",
    "AWAITING_IMPACT_CONFIRMATION",
    "IMPACT_CONFIRMED",
    "REVALIDATING",
    "AWAITING_FINAL_CONFIRMATION",
    "APPLIED",
    "CANCELLED",
    "SUPERSEDED",
}
TERMINAL_STATUSES = {"APPLIED", "CANCELLED", "SUPERSEDED"}
OPEN_STATUSES = ALL_STATUSES - TERMINAL_STATUSES
IMPACT_LEVELS = {
    "NON_SEMANTIC",
    "LOCAL",
    "PROPAGATING",
    "FOUNDATIONAL",
    "IMPACT_UNKNOWN",
}
CONFIRMATION_VALUES = {"PENDING", "CONFIRMED"}
POST_COMMIT_VALUES = {"PENDING", "VERIFIED"}
BLOCKING_VALUES = {"CLEAR", "BLOCKED"}

REQUIRED_KEYS = {
    "contract_version",
    "change_id",
    "status",
    "impact_level",
    "impact_confirmation",
    "final_confirmation",
    "post_commit_verification",
    "blocking_status",
}


class ChangeStateError(ValueError):
    pass


@dataclass(frozen=True)
class ChangeState:
    path: Path
    change_id: str
    status: str
    impact_level: str
    impact_confirmation: str
    final_confirmation: str
    post_commit_verification: str
    blocking_status: str


def _split_frontmatter(text: str) -> tuple[list[str], str]:
    if not text.startswith("---\n"):
        raise ChangeStateError("change record is missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ChangeStateError("change record frontmatter is not closed")
    return text[4:end].splitlines(), text[end + 5:]


def _parse_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw in lines:
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def _state_from_fields(path: Path, fields: dict[str, str]) -> ChangeState:
    path = Path(path)
    if not CHANGE_FILE_RE.fullmatch(path.name):
        raise ChangeStateError(f"invalid change filename: {path.name}")
    missing = sorted(REQUIRED_KEYS - fields.keys())
    if missing:
        raise ChangeStateError(f"missing change fields: {', '.join(missing)}")
    change_id = fields["change_id"]
    if not CHANGE_ID_RE.fullmatch(change_id):
        raise ChangeStateError(f"invalid change_id: {change_id}")
    if path.stem != change_id:
        raise ChangeStateError("change filename does not match change_id")
    if fields["contract_version"] != "0.8":
        raise ChangeStateError("unsupported change contract_version")
    if fields["status"] not in ALL_STATUSES:
        raise ChangeStateError(f"invalid change status: {fields['status']}")
    if fields["impact_level"] not in IMPACT_LEVELS:
        raise ChangeStateError(f"invalid impact level: {fields['impact_level']}")
    if fields["impact_confirmation"] not in CONFIRMATION_VALUES:
        raise ChangeStateError("invalid impact_confirmation")
    if fields["final_confirmation"] not in CONFIRMATION_VALUES:
        raise ChangeStateError("invalid final_confirmation")
    if fields["post_commit_verification"] not in POST_COMMIT_VALUES:
        raise ChangeStateError("invalid post_commit_verification")
    if fields["blocking_status"] not in BLOCKING_VALUES:
        raise ChangeStateError("invalid blocking_status")
    return ChangeState(
        path=path,
        change_id=change_id,
        status=fields["status"],
        impact_level=fields["impact_level"],
        impact_confirmation=fields["impact_confirmation"],
        final_confirmation=fields["final_confirmation"],
        post_commit_verification=fields["post_commit_verification"],
        blocking_status=fields["blocking_status"],
    )


def load_change(path: Path) -> ChangeState:
    path = Path(path)
    lines, _ = _split_frontmatter(path.read_text(encoding="utf-8"))
    return _state_from_fields(path, _parse_fields(lines))


def iter_changes(ba_dir: Path) -> list[ChangeState]:
    changes_dir = Path(ba_dir) / "changes"
    if not changes_dir.is_dir():
        return []
    return [load_change(path) for path in sorted(changes_dir.glob("CHG-*.md"))]


def open_changes(ba_dir: Path) -> list[ChangeState]:
    return [item for item in iter_changes(ba_dir) if item.status in OPEN_STATUSES]


def rewrite_change_frontmatter(path: Path, **updates: str) -> None:
    path = Path(path)
    lines, body = _split_frontmatter(path.read_text(encoding="utf-8"))
    fields = _parse_fields(lines)
    unknown = sorted(set(updates) - set(fields))
    if unknown:
        raise ChangeStateError(f"cannot add unknown frontmatter fields: {', '.join(unknown)}")
    fields.update(updates)
    _state_from_fields(path, fields)
    ordered = []
    for raw in lines:
        if ":" not in raw:
            ordered.append(raw)
            continue
        key = raw.split(":", 1)[0].strip()
        ordered.append(f"{key}: {fields[key]}")
    path.write_text("---\n" + "\n".join(ordered) + "\n---\n" + body, encoding="utf-8")
    load_change(path)
