from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

try:
    from scripts.ba_lint import lint_project
    from scripts.change_state import load_change, ChangeStateError
except ModuleNotFoundError:  # direct `python scripts/ba_eval.py` execution
    from ba_lint import lint_project
    from change_state import load_change, ChangeStateError

ALLOWED_EVENT_TYPES = {"USER", "ASSISTANT", "INSPECT", "RESEARCH", "STATE_WRITE", "APPROVAL"}
ALLOWED_LEVELS = {"must-pass", "diagnostic"}
ALLOWED_STATUSES = {"PASS", "FAIL", "NOT_OBSERVED", "NOT_APPLICABLE"}


class EvaluationError(ValueError):
    pass


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EvaluationError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EvaluationError(f"invalid JSON in {path}: {exc}") from exc


def load_run_record(path: Path) -> dict[str, Any]:
    data = _load_json(Path(path))
    if not isinstance(data, dict):
        raise EvaluationError("run record must be a JSON object")
    for key in ("scenario_id", "runtime", "events"):
        if key not in data:
            raise EvaluationError(f"run record missing required field: {key}")
    if not isinstance(data["scenario_id"], str) or not data["scenario_id"].strip():
        raise EvaluationError("scenario_id must be a non-empty string")
    if not isinstance(data["runtime"], str) or not data["runtime"].strip():
        raise EvaluationError("runtime must be a non-empty string")
    if not isinstance(data["events"], list):
        raise EvaluationError("events must be an array")
    for index, event in enumerate(data["events"]):
        if not isinstance(event, dict):
            raise EvaluationError(f"event {index} must be an object")
        event_type = event.get("type")
        if event_type not in ALLOWED_EVENT_TYPES:
            raise EvaluationError(f"event {index} has invalid type: {event_type!r}")
    telemetry = data.get("telemetry")
    if telemetry is not None and not isinstance(telemetry, dict):
        raise EvaluationError("telemetry must be an object when present")
    return data


def load_expectations(scenario_dir: Path) -> dict[str, Any]:
    scenario_dir = Path(scenario_dir)
    if not scenario_dir.is_dir():
        raise EvaluationError(f"unknown scenario: {scenario_dir}")
    data = _load_json(scenario_dir / "expectations.json")
    if not isinstance(data, dict) or not isinstance(data.get("expectations"), list):
        raise EvaluationError("scenario expectations must contain an expectations array")
    if data.get("scenario_id") != scenario_dir.name:
        raise EvaluationError("scenario_id does not match scenario directory")
    for index, item in enumerate(data["expectations"]):
        if not isinstance(item, dict):
            raise EvaluationError(f"expectation {index} must be an object")
        required = {"criterion", "level", "check", "params", "semantic_review"}
        missing = sorted(required - item.keys())
        if missing:
            raise EvaluationError(f"expectation {index} missing: {', '.join(missing)}")
        if item["level"] not in ALLOWED_LEVELS:
            raise EvaluationError(f"expectation {index} has invalid level")
        if not isinstance(item["params"], dict) or not isinstance(item["semantic_review"], bool):
            raise EvaluationError(f"expectation {index} has invalid params/semantic_review")
    return data


def _events_complete(run: dict[str, Any]) -> bool:
    telemetry = run.get("telemetry") or {}
    return telemetry.get("events_complete") is True


def _contains(value: str | None, needle: str) -> bool:
    return needle.lower() in (value or "").lower()


def _result(criterion: str, status: str, evidence: list[str] | None = None, notes: str = "") -> dict[str, Any]:
    if status not in ALLOWED_STATUSES:
        raise EvaluationError(f"invalid result status: {status}")
    return {"criterion": criterion, "status": status, "evidence": evidence or [], "notes": notes}


def _check_inspect_before_question(item: dict[str, Any], run: dict[str, Any], project: Path | None) -> dict[str, Any]:
    criterion = item["criterion"]
    if not _events_complete(run):
        return _result(criterion, "NOT_OBSERVED", notes="Tool/action telemetry is not declared complete.")
    params = item["params"]
    target = str(params.get("target_contains", ""))
    markers = [str(x).lower() for x in params.get("question_markers", [])]
    inspect_index = None
    question_index = None
    for index, event in enumerate(run["events"]):
        if event["type"] == "INSPECT" and _contains(event.get("target"), target):
            inspect_index = index if inspect_index is None else inspect_index
        if event["type"] == "ASSISTANT":
            text = str(event.get("text", "")).lower()
            if markers and any(marker in text for marker in markers):
                question_index = index if question_index is None else question_index
    if inspect_index is None:
        return _result(criterion, "FAIL", [f"No INSPECT event matched {target!r} before relying on user input."])
    if question_index is not None and question_index < inspect_index:
        return _result(
            criterion,
            "FAIL",
            [f"Relevant user question occurred at event {question_index} before evidence inspection at event {inspect_index}."],
        )
    evidence = [f"INSPECT {target} occurred at event {inspect_index}."]
    if question_index is not None:
        evidence.append(f"First matching user question occurred later at event {question_index}.")
    else:
        evidence.append("No matching retrievable-fact question occurred before/after inspection.")
    return _result(criterion, "PASS", evidence)


def _check_project_text_contains(item: dict[str, Any], run: dict[str, Any], project: Path | None) -> dict[str, Any]:
    criterion = item["criterion"]
    if project is None:
        return _result(criterion, "NOT_OBSERVED", notes="Final project state was not provided.")
    rel = Path(str(item["params"].get("path", "")))
    path = project / rel
    if not path.is_file():
        return _result(criterion, "FAIL", [f"Expected state file is missing: {rel}"])
    needle = str(item["params"].get("text", ""))
    if needle in path.read_text(encoding="utf-8"):
        return _result(criterion, "PASS", [f"{rel} contains required provenance marker {needle!r}."])
    return _result(criterion, "FAIL", [f"{rel} does not contain required marker {needle!r}."])


def _check_path_absent(item: dict[str, Any], run: dict[str, Any], project: Path | None) -> dict[str, Any]:
    criterion = item["criterion"]
    if project is None:
        return _result(criterion, "NOT_OBSERVED", notes="Final project state was not provided.")
    pattern = str(item["params"].get("path", ""))
    if any(ch in pattern for ch in "*?["):
        matches = sorted(project.glob(pattern))
        if matches:
            rels = [str(path.relative_to(project)) for path in matches]
            return _result(criterion, "FAIL", [f"Forbidden path(s) exist: {', '.join(rels)}"])
        return _result(criterion, "PASS", [f"Skipped phase did not create any path matching {pattern}."])
    rel = Path(pattern)
    if (project / rel).exists():
        return _result(criterion, "FAIL", [f"Forbidden path exists: {rel}"])
    return _result(criterion, "PASS", [f"Skipped phase did not create {rel}."])


def _record_status(project: Path, record_id: str) -> str | None:
    block_re = re.compile(r"```yaml\s+ba-record\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
    for rel in (".ba/REQUIREMENTS.md", ".ba/DECISIONS.md"):
        path = project / rel
        if not path.is_file():
            continue
        for match in block_re.finditer(path.read_text(encoding="utf-8")):
            fields: dict[str, str] = {}
            for raw in match.group(1).splitlines():
                if ":" not in raw:
                    continue
                key, value = raw.split(":", 1)
                fields[key.strip()] = value.strip().strip('"').strip("'")
            if fields.get("id") == record_id:
                return fields.get("status")
    return None


def _check_record_status_not(item: dict[str, Any], run: dict[str, Any], project: Path | None) -> dict[str, Any]:
    criterion = item["criterion"]
    if project is None:
        return _result(criterion, "NOT_OBSERVED", notes="Final project state was not provided.")
    record_id = str(item["params"].get("record_id", ""))
    forbidden = str(item["params"].get("status", ""))
    actual = _record_status(project, record_id)
    if actual is None:
        return _result(criterion, "NOT_OBSERVED", notes=f"Record {record_id} was not present in final state.")
    if actual == forbidden:
        return _result(criterion, "FAIL", [f"{record_id} was {actual}; uncertain input was promoted to forbidden status."])
    return _result(criterion, "PASS", [f"{record_id} remained {actual}, not {forbidden}."])


def _check_no_state_create(item: dict[str, Any], run: dict[str, Any], project: Path | None) -> dict[str, Any]:
    criterion = item["criterion"]
    if not _events_complete(run):
        return _result(criterion, "NOT_OBSERVED", notes="State-write telemetry is not declared complete.")
    target = str(item["params"].get("target_contains", ""))
    violations = []
    for index, event in enumerate(run["events"]):
        if event["type"] != "STATE_WRITE":
            continue
        if _contains(event.get("target"), target) and str(event.get("operation", "")).upper() == "CREATE":
            violations.append(f"CREATE {event.get('target')} at event {index}")
    if violations:
        return _result(criterion, "FAIL", violations)
    return _result(criterion, "PASS", [f"No CREATE write targeted {target!r}."])


def _check_event_present(item: dict[str, Any], run: dict[str, Any], project: Path | None) -> dict[str, Any]:
    criterion = item["criterion"]
    if not _events_complete(run):
        return _result(criterion, "NOT_OBSERVED", notes="Event telemetry is not declared complete.")
    expected_type = str(item["params"].get("type", ""))
    target = str(item["params"].get("target_contains", ""))
    for index, event in enumerate(run["events"]):
        if event["type"] == expected_type and (not target or _contains(event.get("target"), target)):
            return _result(criterion, "PASS", [f"Observed {expected_type} at event {index}: {event.get('target', '')}"])
    return _result(criterion, "FAIL", [f"No {expected_type} event matched {target!r}."])


def _check_approval_before_state_write(item: dict[str, Any], run: dict[str, Any], project: Path | None) -> dict[str, Any]:
    criterion = item["criterion"]
    if not _events_complete(run):
        return _result(criterion, "NOT_OBSERVED", notes="Approval/state-write telemetry is not declared complete.")
    target = str(item["params"].get("target_contains", ".ba/phases/"))
    write_index = None
    approval_index = None
    for index, event in enumerate(run["events"]):
        if event["type"] == "APPROVAL" and approval_index is None:
            approval_index = index
        if event["type"] == "STATE_WRITE" and _contains(event.get("target"), target) and write_index is None:
            write_index = index
    if write_index is None:
        return _result(criterion, "NOT_APPLICABLE", notes="No approved snapshot write occurred in this run.")
    if approval_index is None or approval_index > write_index:
        return _result(criterion, "FAIL", [f"Snapshot write at event {write_index} occurred without prior explicit APPROVAL."])
    return _result(criterion, "PASS", [f"APPROVAL at event {approval_index} preceded snapshot write at event {write_index}."])


def _check_project_text_absent(item: dict[str, Any], run: dict[str, Any], project: Path | None) -> dict[str, Any]:
    criterion = item["criterion"]
    if project is None:
        return _result(criterion, "NOT_OBSERVED", notes="Final project state was not provided.")
    rel = Path(str(item["params"].get("path", "")))
    path = project / rel
    if not path.is_file():
        return _result(criterion, "PASS", [f"{rel} is absent, so forbidden text is absent."])
    needle = str(item["params"].get("text", ""))
    if needle in path.read_text(encoding="utf-8"):
        return _result(criterion, "FAIL", [f"{rel} contains forbidden marker {needle!r}."])
    return _result(criterion, "PASS", [f"{rel} does not contain forbidden marker {needle!r}."])


def _check_change_status(item: dict[str, Any], run: dict[str, Any], project: Path | None) -> dict[str, Any]:
    criterion = item["criterion"]
    if project is None:
        return _result(criterion, "NOT_OBSERVED", notes="Final project state was not provided.")
    change_id = str(item["params"].get("change_id", ""))
    expected = str(item["params"].get("status", ""))
    path = project / ".ba/changes" / f"{change_id}.md"
    if not path.is_file():
        return _result(criterion, "FAIL", [f"Change record is missing: {change_id}"])
    try:
        actual = load_change(path).status
    except ChangeStateError as exc:
        return _result(criterion, "FAIL", [f"Invalid change record {change_id}: {exc}"])
    if actual != expected:
        return _result(criterion, "FAIL", [f"{change_id} status is {actual}, expected {expected}."])
    return _result(criterion, "PASS", [f"{change_id} status is {expected}."])


def _check_inspect_before_state_write(item: dict[str, Any], run: dict[str, Any], project: Path | None) -> dict[str, Any]:
    criterion = item["criterion"]
    if not _events_complete(run):
        return _result(criterion, "NOT_OBSERVED", notes="Inspect/state-write telemetry is not declared complete.")
    inspect_target = str(item["params"].get("inspect_target", item["params"].get("target_contains", "")))
    write_target = str(item["params"].get("write_target", item["params"].get("target_contains", "")))
    inspect_index = next((i for i, e in enumerate(run["events"]) if e["type"] == "INSPECT" and _contains(e.get("target"), inspect_target)), None)
    write_index = next((i for i, e in enumerate(run["events"]) if e["type"] == "STATE_WRITE" and _contains(e.get("target"), write_target)), None)
    if write_index is None:
        return _result(criterion, "NOT_APPLICABLE", notes="No matching state write occurred.")
    if inspect_index is None or inspect_index > write_index:
        return _result(criterion, "FAIL", [f"Write at event {write_index} occurred without prior INSPECT for {inspect_target!r}."])
    return _result(criterion, "PASS", [f"INSPECT at event {inspect_index} preceded write at event {write_index}."])


def _check_approval_scope_before_state_write(item: dict[str, Any], run: dict[str, Any], project: Path | None) -> dict[str, Any]:
    criterion = item["criterion"]
    if not _events_complete(run):
        return _result(criterion, "NOT_OBSERVED", notes="Approval/state-write telemetry is not declared complete.")
    scope = str(item["params"].get("scope", ""))
    target = str(item["params"].get("target_contains", ""))
    approval = next((i for i, e in enumerate(run["events"]) if e["type"] == "APPROVAL" and e.get("scope") == scope), None)
    write = next((i for i, e in enumerate(run["events"]) if e["type"] == "STATE_WRITE" and _contains(e.get("target"), target)), None)
    if write is None:
        return _result(criterion, "NOT_APPLICABLE", notes="No matching canonical write occurred.")
    if approval is None or approval > write:
        return _result(criterion, "FAIL", [f"{scope} approval did not precede write at event {write}."])
    return _result(criterion, "PASS", [f"{scope} approval at event {approval} preceded write at event {write}."])


def _check_inspect_after_state_write(item: dict[str, Any], run: dict[str, Any], project: Path | None) -> dict[str, Any]:
    criterion = item["criterion"]
    if not _events_complete(run):
        return _result(criterion, "NOT_OBSERVED", notes="Readback telemetry is not declared complete.")
    target = str(item["params"].get("target_contains", ""))
    write = next((i for i, e in enumerate(run["events"]) if e["type"] == "STATE_WRITE" and _contains(e.get("target"), target)), None)
    if write is None:
        return _result(criterion, "NOT_APPLICABLE", notes="No matching state write occurred.")
    inspect = next((i for i, e in enumerate(run["events"][write + 1:], start=write + 1) if e["type"] == "INSPECT" and _contains(e.get("target"), target)), None)
    if inspect is None:
        return _result(criterion, "FAIL", [f"No readback INSPECT after write at event {write}."])
    return _result(criterion, "PASS", [f"Readback INSPECT occurred at event {inspect}."])


def _check_visual_selection(item, run, project):
    criterion = item["criterion"]
    if not _events_complete(run):
        return _result(criterion, "NOT_OBSERVED", notes="Complete captured action telemetry required.")
    expected = item["params"]["kind"]
    selected = [event for event in run["events"] if event["type"] == "ASSISTANT" and event.get("operation") == "visual_selection"]
    writes = [event for event in run["events"] if event["type"] == "STATE_WRITE" and str(event.get("target", "")).replace(chr(92), "/").endswith("docs/BA-Workspace.html")]
    if expected == "text":
        valid = not writes and all(event.get("visual_kind") == "text" for event in selected)
    else:
        valid = bool(selected and writes) and selected[-1].get("visual_kind") == expected
    return _result(criterion, "PASS" if valid else "FAIL",
                   [f"Expected {expected}; observed selections {len(selected)}, workspace writes {len(writes)}."])


CHECKS = {
    "visual_selection": _check_visual_selection,
    "inspect_before_question": _check_inspect_before_question,
    "project_text_contains": _check_project_text_contains,
    "path_absent": _check_path_absent,
    "record_status_not": _check_record_status_not,
    "no_state_create": _check_no_state_create,
    "event_present": _check_event_present,
    "approval_before_state_write": _check_approval_before_state_write,
    "project_text_absent": _check_project_text_absent,
    "change_status": _check_change_status,
    "inspect_before_state_write": _check_inspect_before_state_write,
    "approval_scope_before_state_write": _check_approval_scope_before_state_write,
    "inspect_after_state_write": _check_inspect_after_state_write,
}


def evaluate_run(scenario_dir: Path, run_path: Path, project_dir: Path | None) -> dict[str, Any]:
    scenario_dir = Path(scenario_dir)
    expectations = load_expectations(scenario_dir)
    run = load_run_record(Path(run_path))
    if run["scenario_id"] != expectations["scenario_id"]:
        raise EvaluationError(
            f"run scenario_id {run['scenario_id']!r} does not match scenario {expectations['scenario_id']!r}"
        )
    project = Path(project_dir).resolve() if project_dir is not None else None
    criteria: list[dict[str, Any]] = []
    semantic_review: list[dict[str, Any]] = []
    levels: dict[str, str] = {}
    for item in expectations["expectations"]:
        criterion = item["criterion"]
        levels[criterion] = item["level"]
        if item["semantic_review"] or item["check"] == "semantic":
            result = _result(criterion, "NOT_OBSERVED", notes="Requires criterion-level semantic review.")
            semantic_review.append({
                "criterion": criterion,
                "level": item["level"],
                "prompt": item.get("review_prompt", "Review this criterion against transcript evidence."),
            })
        else:
            check = CHECKS.get(item["check"])
            if check is None:
                raise EvaluationError(f"unsupported deterministic check: {item['check']}")
            result = check(item, run, project)
        result["level"] = item["level"]
        criteria.append(result)

    if project is None:
        lint = {"status": "NOT_OBSERVED", "errors": 0, "warnings": 0, "diagnostics": []}
        state_integrity = "NOT_OBSERVED"
    else:
        lint_result = lint_project(project)
        lint = {
            "status": "FAIL" if lint_result.error_count else "PASS",
            "errors": lint_result.error_count,
            "warnings": lint_result.warning_count,
            "diagnostics": [
                {"severity": d.severity, "code": d.code, "message": d.message, "path": d.path}
                for d in lint_result.diagnostics
            ],
        }
        state_integrity = lint["status"]

    must_pass_failures = sum(
        1 for result in criteria if levels.get(result["criterion"]) == "must-pass" and result["status"] == "FAIL"
    )
    must_pass_unobserved = sum(
        1 for result in criteria if levels.get(result["criterion"]) == "must-pass" and result["status"] == "NOT_OBSERVED"
    )
    if state_integrity == "FAIL":
        must_pass_failures += 1

    return {
        "scenario_id": expectations["scenario_id"],
        "runtime": run["runtime"],
        "model": run.get("model"),
        "criteria": criteria,
        "semantic_review": semantic_review,
        "lint": lint,
        "state_integrity": state_integrity,
        "must_pass_failures": must_pass_failures,
        "must_pass_unobserved": must_pass_unobserved,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate a normalized BA Discovery behavioral run")
    parser.add_argument("--scenario", required=True, help="Scenario directory")
    parser.add_argument("--run", required=True, help="Normalized run JSON")
    parser.add_argument("--project", help="Final project directory containing .ba/")
    parser.add_argument("--json-out", help="Optional output JSON file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        result = evaluate_run(
            Path(args.scenario),
            Path(args.run),
            Path(args.project) if args.project else None,
        )
    except EvaluationError as exc:
        print(f"ba-eval: {exc}", file=sys.stderr)
        return 2
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        Path(args.json_out).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 1 if result["must_pass_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
