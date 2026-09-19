from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile

try:
    from scripts.ba_lint import lint_project
    from scripts.change_state import load_change, rewrite_change_frontmatter
except ModuleNotFoundError:
    from ba_lint import lint_project
    from change_state import load_change, rewrite_change_frontmatter

ALLOWED_CANONICAL = {"PROJECT.md", "REQUIREMENTS.md", "DECISIONS.md", "RESEARCH.md"}


class ChangeCommitError(RuntimeError):
    pass


def _replace_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp-ba-change")
    tmp.write_bytes(payload)
    tmp.replace(path)


def _candidate_files(candidate_dir: Path) -> list[Path]:
    candidate_dir = Path(candidate_dir)
    if not candidate_dir.is_dir():
        raise ChangeCommitError("candidate directory does not exist")
    files = sorted(p for p in candidate_dir.iterdir() if p.is_file())
    invalid = [p.name for p in files if p.name not in ALLOWED_CANONICAL]
    if invalid:
        raise ChangeCommitError(f"candidate contains non-canonical file(s): {', '.join(invalid)}")
    if not files:
        raise ChangeCommitError("candidate contains no canonical files")
    return files


def _expected_candidate_dir(root: Path, change_id: str) -> Path:
    return (root / ".ba/changes/.candidate" / change_id).resolve()


def _assert_candidate_location(root: Path, change_id: str, candidate_dir: Path) -> None:
    if Path(candidate_dir).resolve() != _expected_candidate_dir(root, change_id):
        raise ChangeCommitError("candidate directory must be .ba/changes/.candidate/<change_id>")


def validate_candidate(project_root: Path, change_id: str, candidate_dir: Path) -> None:
    root = Path(project_root).resolve()
    candidate_dir = Path(candidate_dir).resolve()
    _assert_candidate_location(root, change_id, candidate_dir)
    change_path = root / ".ba/changes" / f"{change_id}.md"
    state = load_change(change_path)
    if state.status != "AWAITING_FINAL_CONFIRMATION":
        raise ChangeCommitError("change is not awaiting final confirmation")
    if state.impact_confirmation != "CONFIRMED":
        raise ChangeCommitError("impact confirmation is not confirmed")
    if state.final_confirmation != "CONFIRMED":
        raise ChangeCommitError("final confirmation is not confirmed")
    if state.blocking_status != "CLEAR":
        raise ChangeCommitError("blocking items remain")

    files = _candidate_files(candidate_dir)
    with tempfile.TemporaryDirectory(prefix="ba-change-") as tmp:
        shadow_root = Path(tmp) / "project"
        shutil.copytree(root / ".ba", shadow_root / ".ba")
        # The candidate working directory is staging noise, not project truth.
        shutil.rmtree(shadow_root / ".ba/changes/.candidate", ignore_errors=True)
        for source in files:
            shutil.copy2(source, shadow_root / ".ba" / source.name)
        lint = lint_project(shadow_root)
        if lint.error_count:
            codes = ", ".join(d.code for d in lint.diagnostics if d.severity == "ERROR")
            raise ChangeCommitError(f"prospective state failed lint: {codes}")


def _append_applied_result(change_path: Path, touched: tuple[str, ...]) -> None:
    text = change_path.read_text(encoding="utf-8")
    if "## Applied Result" in text:
        return
    lines = "\n".join(f"- `{item}`" for item in touched)
    change_path.write_text(
        text.rstrip()
        + "\n\n## Applied Result\n\n"
        + "Canonical files applied and exact-byte readback verified:\n"
        + lines
        + "\n",
        encoding="utf-8",
    )


def apply_candidate(project_root: Path, change_id: str, candidate_dir: Path) -> tuple[str, ...]:
    root = Path(project_root).resolve()
    candidate_dir = Path(candidate_dir).resolve()
    validate_candidate(root, change_id, candidate_dir)

    change_path = root / ".ba/changes" / f"{change_id}.md"
    files = _candidate_files(candidate_dir)
    targets = [root / ".ba" / p.name for p in files]
    backups = {target: target.read_bytes() if target.exists() else None for target in targets}
    original_change = change_path.read_bytes()
    touched = tuple(f".ba/{p.name}" for p in files)

    try:
        for source in files:
            target = root / ".ba" / source.name
            _replace_bytes(target, source.read_bytes())

        for source in files:
            target = root / ".ba" / source.name
            if target.read_bytes() != source.read_bytes():
                raise ChangeCommitError(f"post-commit readback mismatch: {target.name}")

        _append_applied_result(change_path, touched)
        rewrite_change_frontmatter(
            change_path,
            status="APPLIED",
            post_commit_verification="VERIFIED",
        )

        final_lint = lint_project(root)
        if final_lint.error_count:
            codes = ", ".join(d.code for d in final_lint.diagnostics if d.severity == "ERROR")
            raise ChangeCommitError(f"final state failed lint: {codes}")

    except Exception as exc:
        for target, payload in backups.items():
            if payload is None:
                target.unlink(missing_ok=True)
            else:
                _replace_bytes(target, payload)
        _replace_bytes(change_path, original_change)
        if isinstance(exc, ChangeCommitError):
            raise ChangeCommitError(f"{exc}; rolled back") from exc
        raise ChangeCommitError(f"{exc}; rolled back") from exc

    shutil.rmtree(candidate_dir)
    return touched


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate/apply a BA Discovery staged change")
    parser.add_argument("--project", required=True)
    parser.add_argument("--change", required=True)
    parser.add_argument("--candidate-dir", required=True)
    parser.add_argument("--apply", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.apply:
            touched = apply_candidate(Path(args.project), args.change, Path(args.candidate_dir))
            print("ba-change-commit: applied " + ", ".join(touched))
        else:
            validate_candidate(Path(args.project), args.change, Path(args.candidate_dir))
            print("ba-change-commit: prospective state valid")
        return 0
    except ChangeCommitError as exc:
        print(f"ba-change-commit: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
