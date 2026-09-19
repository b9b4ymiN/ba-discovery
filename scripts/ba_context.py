from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from scripts.change_state import open_changes
except ModuleNotFoundError:
    from change_state import open_changes

CURRENT_FILES = (
    ".ba/PROJECT.md",
    ".ba/REQUIREMENTS.md",
    ".ba/DECISIONS.md",
    ".ba/RESEARCH.md",
)


def build_context(
    project_root: Path,
    focus_change: str | None = None,
    identity_review: bool = False,
) -> dict:
    root = Path(project_root).resolve()
    current = [rel for rel in CURRENT_FILES if (root / rel).is_file()]
    open_items = open_changes(root / ".ba")
    open_paths = [f".ba/changes/{item.path.name}" for item in open_items]

    selected: list[str] = []
    focus_status = "CURRENT_ONLY"
    if identity_review:
        selected = open_paths
        focus_status = "IDENTITY_REVIEW"
    elif focus_change:
        wanted = f".ba/changes/{focus_change}.md"
        if wanted in open_paths:
            selected = [wanted]
            focus_status = "OPEN"
        else:
            focus_status = "NOT_OPEN"

    return {
        "current": current,
        "open_changes": open_paths,
        "selected_changes": selected,
        "read_set": current + selected,
        "history_loaded": False,
        "focus_status": focus_status,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build BA Discovery current working context")
    parser.add_argument("--project", required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--focus-change")
    group.add_argument("--identity-review", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(
        build_context(
            Path(args.project),
            focus_change=args.focus_change,
            identity_review=args.identity_review,
        ),
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
