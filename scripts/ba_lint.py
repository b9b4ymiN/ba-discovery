from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Literal

try:
    from scripts.change_state import ChangeStateError, load_change
except ModuleNotFoundError:
    from change_state import ChangeStateError, load_change

Severity = Literal["ERROR", "WARNING"]

ID_RE = re.compile(r"(?m)^#{1,6}\s+(NEED|REQ|CON|DEC)-([0-9]{4,})\b")
ID_FIELD_RE = re.compile(r"(?m)^id:\s*((?:NEED|REQ|CON|DEC)-[0-9]{4,})\s*$")
RECORD_BLOCK_RE = re.compile(r"```yaml\s+ba-record\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
REF_FIELD_RE = re.compile(r"(?m)^(derived_from|superseded_by|related):\s*(.*?)\s*$")
ID_TOKEN_RE = re.compile(r"\b(?:NEED|REQ|CON|DEC)-[0-9]{4,}\b")
CHG_TOKEN_RE = re.compile(r"\bCHG-[0-9]{4,}\b")
PHASE_LINE_RE = re.compile(r"(?m)^current_phase:\s*([A-Z_]+)\s*$")
BASELINE_SECTION_RE = re.compile(r"(?ms)^## Current Baselines\s*\n(.*?)(?=^##\s|\Z)")
BASELINE_PATH_RE = re.compile(r"\.ba/phases/[A-Za-z0-9_.-]+/R[0-9]{3}\.md")
SNAPSHOT_RE = re.compile(r"^R[0-9]{3}\.md$")
CONTRACT_V06_RE = re.compile(r"(?m)^contract_version:\s*0\.6(?:\.[0-9]+)?\s*$")

PHASES = {"UNDERSTAND", "REQUIREMENTS", "DESIGN", "SPEC"}
LEGACY_PHASES = {"BACKGROUND_DISCOVERY", "REQUIREMENT_DISCOVERY", "SYSTEM_DESIGN", "FINAL_FRD"}
REQ_STATES = {
    "DISCOVERED",
    "CLARIFYING",
    "CANDIDATE",
    "CONFIRMED",
    "READY_FOR_DESIGN",
    "NEEDS_RECONFIRMATION",
    "SUPERSEDED",
    "REJECTED",
}
DEC_STATES = {"PROPOSED", "CONFIRMED", "REJECTED", "NEEDS_RECONFIRMATION", "SUPERSEDED"}


@dataclass(frozen=True)
class Diagnostic:
    severity: Severity
    code: str
    message: str
    path: str | None = None


@dataclass(frozen=True)
class LintResult:
    diagnostics: tuple[Diagnostic, ...]

    @property
    def error_count(self) -> int:
        return sum(d.severity == "ERROR" for d in self.diagnostics)

    @property
    def warning_count(self) -> int:
        return sum(d.severity == "WARNING" for d in self.diagnostics)


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _canonical_files(ba: Path) -> list[Path]:
    return [p for p in (ba / "REQUIREMENTS.md", ba / "DECISIONS.md") if p.is_file()]


def _declared_ids(path: Path) -> list[str]:
    text = _read(path)
    heading_ids = [f"{m.group(1)}-{m.group(2)}" for m in ID_RE.finditer(text)]
    # Explicit ID fields support files that choose field-first records. Avoid double-counting
    # a normal heading + matching field declaration for the same record.
    field_ids = [m.group(1) for m in ID_FIELD_RE.finditer(text)]
    heading_counts: dict[str, int] = {}
    for record_id in heading_ids:
        heading_counts[record_id] = heading_counts.get(record_id, 0) + 1
    field_only = [record_id for record_id in field_ids if record_id not in heading_counts]
    return heading_ids + field_only


def collect_record_declarations(ba: Path, root: Path) -> tuple[dict[str, str], list[Diagnostic]]:
    declarations: dict[str, str] = {}
    diagnostics: list[Diagnostic] = []
    for path in _canonical_files(ba):
        for record_id in _declared_ids(path):
            if record_id in declarations:
                diagnostics.append(
                    Diagnostic(
                        "ERROR",
                        "DUPLICATE_ID",
                        f"Duplicate canonical ID {record_id}",
                        _rel(path, root),
                    )
                )
            else:
                declarations[record_id] = _rel(path, root)
    return declarations, diagnostics


def collect_explicit_references(ba: Path, root: Path) -> list[tuple[str, str, str]]:
    references: list[tuple[str, str, str]] = []
    for path in _canonical_files(ba):
        text = _read(path)
        for match in REF_FIELD_RE.finditer(text):
            field, value = match.group(1), match.group(2)
            if value.strip().lower() in {"null", "none", "[]"}:
                continue
            for record_id in ID_TOKEN_RE.findall(value):
                references.append((record_id, field, _rel(path, root)))
            for change_id in CHG_TOKEN_RE.findall(value):
                references.append((change_id, field, _rel(path, root)))
    return references


def _parse_simple_block(block: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in block.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def _check_lifecycle(ba: Path, root: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for path in _canonical_files(ba):
        text = _read(path)
        for match in RECORD_BLOCK_RE.finditer(text):
            record = _parse_simple_block(match.group(1))
            record_id = record.get("id", "")
            status = record.get("status")
            if not record_id or not status:
                continue
            allowed = DEC_STATES if record_id.startswith("DEC-") else REQ_STATES
            if status not in allowed:
                diagnostics.append(
                    Diagnostic(
                        "ERROR",
                        "INVALID_LIFECYCLE_VALUE",
                        f"Invalid lifecycle status {status!r} for {record_id}",
                        _rel(path, root),
                    )
                )
    return diagnostics


def _check_phase(project: Path, root: Path) -> list[Diagnostic]:
    text = _read(project)
    match = PHASE_LINE_RE.search(text)
    if not match:
        return []
    value = match.group(1)
    if value in PHASES:
        return []
    if value in LEGACY_PHASES:
        return [
            Diagnostic(
                "WARNING",
                "LEGACY_PHASE_VALUE",
                f"Legacy current_phase {value}; migrate lazily when current state is next written",
                _rel(project, root),
            )
        ]
    return [Diagnostic("ERROR", "INVALID_PHASE_VALUE", f"Invalid current_phase {value}", _rel(project, root))]


def _check_baselines(project: Path, root: Path) -> list[Diagnostic]:
    text = _read(project)
    section = BASELINE_SECTION_RE.search(text)
    if not section:
        return []
    diagnostics: list[Diagnostic] = []
    for rel_path in BASELINE_PATH_RE.findall(section.group(1)):
        candidate = root / rel_path
        if not candidate.is_file():
            diagnostics.append(
                Diagnostic("ERROR", "MISSING_BASELINE", f"Current baseline does not exist: {rel_path}", _rel(project, root))
            )
    return diagnostics


def check_snapshot_integrity(ba: Path, root: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    phases = ba / "phases"
    if not phases.is_dir():
        return diagnostics
    for phase_dir in sorted(p for p in phases.iterdir() if p.is_dir()):
        seen_revisions: set[str] = set()
        for path in sorted(phase_dir.glob("*.md")):
            if not SNAPSHOT_RE.fullmatch(path.name):
                diagnostics.append(
                    Diagnostic("ERROR", "INVALID_SNAPSHOT_NAME", f"Snapshot filename must match RNNN.md: {path.name}", _rel(path, root))
                )
                continue
            if path.name in seen_revisions:
                diagnostics.append(
                    Diagnostic("ERROR", "DUPLICATE_SNAPSHOT_REVISION", f"Duplicate snapshot revision {path.name}", _rel(path, root))
                )
            seen_revisions.add(path.name)
            text = _read(path)
            if CONTRACT_V06_RE.search(text) and "## Approval" not in text:
                diagnostics.append(
                    Diagnostic("ERROR", "MISSING_APPROVAL_BLOCK", "v0.6+ approved snapshot lacks ## Approval", _rel(path, root))
                )
    return diagnostics


def _frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---", 4)
    return text[4:end] if end != -1 else ""


def _check_bypass_provenance(project: Path, root: Path) -> list[Diagnostic]:
    fm = _frontmatter(_read(project))
    lines = fm.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip().startswith("phase_inputs:"))
    except StopIteration:
        return []
    if lines[start].strip().endswith("[]"):
        return []
    entries: list[list[str]] = []
    current: list[str] = []
    for line in lines[start + 1 :]:
        if line and not line.startswith((" ", "\t")):
            break
        stripped = line.strip()
        if stripped.startswith("- "):
            if current:
                entries.append(current)
            current = [stripped[2:]]
        elif current and stripped:
            current.append(stripped)
    if current:
        entries.append(current)
    diagnostics: list[Diagnostic] = []
    for entry in entries:
        data = _parse_simple_block("\n".join(entry))
        missing = [key for key in ("source", "provenance", "validation") if not data.get(key)]
        if missing:
            diagnostics.append(
                Diagnostic(
                    "ERROR",
                    "MISSING_BYPASS_PROVENANCE",
                    f"phase_inputs entry missing: {', '.join(missing)}",
                    _rel(project, root),
                )
            )
    return diagnostics



def _check_changes(ba: Path, root: Path) -> tuple[set[str], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    change_ids: set[str] = set()
    changes_dir = ba / "changes"
    if not changes_dir.is_dir():
        return change_ids, diagnostics
    for path in sorted(changes_dir.glob("CHG-*.md")):
        try:
            state = load_change(path)
        except ChangeStateError as exc:
            diagnostics.append(Diagnostic("ERROR", "INVALID_CHANGE_RECORD", str(exc), _rel(path, root)))
            continue
        change_ids.add(state.change_id)
        if state.status in {"IMPACT_CONFIRMED", "REVALIDATING", "AWAITING_FINAL_CONFIRMATION", "APPLIED"} and state.impact_confirmation != "CONFIRMED":
            diagnostics.append(Diagnostic("ERROR", "INVALID_IMPACT_CONFIRMATION_STATE", f"{state.change_id} status {state.status} requires impact_confirmation CONFIRMED", _rel(path, root)))
        if state.status == "APPLIED":
            if not (state.impact_confirmation == "CONFIRMED" and state.final_confirmation == "CONFIRMED" and state.post_commit_verification == "VERIFIED" and state.blocking_status == "CLEAR"):
                diagnostics.append(Diagnostic("ERROR", "INVALID_APPLIED_CHANGE_STATE", f"{state.change_id} is APPLIED without complete confirmation/readback state", _rel(path, root)))
            if "## Applied Result" not in _read(path):
                diagnostics.append(Diagnostic("ERROR", "MISSING_APPLIED_RESULT", f"{state.change_id} is APPLIED but lacks ## Applied Result", _rel(path, root)))
    return change_ids, diagnostics


def _check_clean_canonical(ba: Path, root: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for path in _canonical_files(ba):
        text = _read(path)
        for match in RECORD_BLOCK_RE.finditer(text):
            record = _parse_simple_block(match.group(1))
            record_id = record.get("id", "")
            if record_id and record.get("status") == "SUPERSEDED":
                diagnostics.append(Diagnostic("ERROR", "OBSOLETE_RECORD_IN_CANONICAL", f"{record_id} is SUPERSEDED but current canonical must contain only current truth", _rel(path, root)))
    return diagnostics

def lint_project(project_root: Path) -> LintResult:
    root = Path(project_root).resolve()
    ba = root / ".ba"
    if not ba.is_dir():
        return LintResult((Diagnostic("ERROR", "MISSING_PROJECT_BRAIN", "Missing .ba directory", None),))

    diagnostics: list[Diagnostic] = []
    declarations, duplicate_diags = collect_record_declarations(ba, root)
    diagnostics.extend(duplicate_diags)
    change_ids, change_diags = _check_changes(ba, root)
    diagnostics.extend(change_diags)

    for record_id, field, path in collect_explicit_references(ba, root):
        if record_id.startswith("CHG-"):
            if record_id not in change_ids:
                diagnostics.append(Diagnostic("ERROR", "DANGLING_CHANGE_REFERENCE", f"{field} references undeclared {record_id}", path))
        elif record_id not in declarations:
            diagnostics.append(Diagnostic("ERROR", "DANGLING_REFERENCE", f"{field} references undeclared {record_id}", path))

    project = ba / "PROJECT.md"
    if project.is_file():
        diagnostics.extend(_check_phase(project, root))
        diagnostics.extend(_check_baselines(project, root))
        diagnostics.extend(_check_bypass_provenance(project, root))

    diagnostics.extend(_check_lifecycle(ba, root))
    diagnostics.extend(_check_clean_canonical(ba, root))
    diagnostics.extend(check_snapshot_integrity(ba, root))

    return LintResult(tuple(diagnostics))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate BA Discovery .ba structural integrity")
    parser.add_argument("--project", default=".", help="Project root containing .ba/")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_parser().parse_args(argv)
        root = Path(args.project)
        if not root.exists() or not root.is_dir():
            print(f"ba-lint: invalid project directory: {root}", file=sys.stderr)
            return 2
        result = lint_project(root)
    except Exception as exc:  # runtime/invocation failure, not a project diagnostic
        print(f"ba-lint: runtime error: {exc}", file=sys.stderr)
        return 2

    for diagnostic in result.diagnostics:
        location = f" [{diagnostic.path}]" if diagnostic.path else ""
        print(f"{diagnostic.severity} {diagnostic.code}{location}: {diagnostic.message}")
    print(f"ba-lint: {result.error_count} error(s), {result.warning_count} warning(s)")
    return 1 if result.error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
