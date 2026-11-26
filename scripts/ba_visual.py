#!/usr/bin/env python3
"""Assemble a read-only offline visual draft. Never modifies .ba/."""
import argparse
import base64
import hashlib
import html
import json
from pathlib import Path
import re
import sys

ASSETS = Path(__file__).resolve().parents[1] / "assets" / "visual"
PELE_VERSION = "1.7.0"
MARKER = '<meta name="ba-visual-format" content="1">'
MATRIX = json.loads((ASSETS / "selection-matrix.json").read_text(encoding="utf-8"))
STATUSES = {"OBSERVED", "APPROVED", "PROPOSED", "ASSUMPTION", "ILLUSTRATIVE"}
TABLE_KINDS = {"decision_table", "comparison", "before_after", "traceability"}
PREFIXES = {
    "flowchart": r"^(?:flowchart|graph)\s",
    "swimlane": r"^(?:flowchart|graph)\s",
    "sequence": r"^sequenceDiagram\b",
    "erd": r"^erDiagram\b",
    "state": r"^stateDiagram(?:-v2)?\b",
    "architecture": r"^(?:architecture-beta\b|(?:flowchart|graph)\s)",
    "cause_map": r"^(?:flowchart|graph)\s",
    "impact_graph": r"^(?:flowchart|graph)\s",
}
PHASES = {"UNDERSTAND", "REQUIREMENTS", "DESIGN", "SPEC", "CHANGE"}
MAX_SOURCE = 100_000
MAX_DIAGRAMS = 30
MAX_INPUT_BYTES = 2_000_000
DATA_RE = re.compile(r'<script id="ba-data" type="application/json">(.*?)</script>', re.S)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def source_path(project, name):
    if not isinstance(name, str) or not name:
        raise ValueError("Source path must be a nonempty string")
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != ".ba":
        raise ValueError("Source must be a relative .ba/ path: " + name)
    resolved = (project / path).resolve()
    if not resolved.is_relative_to(project / ".ba") or not resolved.is_file():
        raise ValueError("Source is missing or outside .ba/: " + name)
    return resolved


def fingerprint(project, names):
    if not isinstance(names, list) or any(not isinstance(n, str) for n in names):
        raise ValueError("sources must be an array of paths")
    return [{"path": n, "sha256": digest(source_path(project, n).read_bytes())}
            for n in sorted(set(names))]


def field(obj, key, default=None, limit=MAX_SOURCE):
    value = obj.get(key, default)
    if not isinstance(value, str) or len(value) > limit:
        raise ValueError("Invalid text field: " + key)
    return value


def normalize(project, spec):
    if not isinstance(spec, dict):
        raise ValueError("Input must be an object")
    phase = field(spec, "phase", limit=30)
    if phase not in PHASES:
        raise ValueError("Invalid phase")
    diagrams = spec.get("diagrams", [])
    if not isinstance(diagrams, list) or len(diagrams) > MAX_DIAGRAMS:
        raise ValueError("Invalid diagrams array")
    normalized = []
    for item in diagrams:
        if not isinstance(item, dict):
            raise ValueError("Diagram must be an object")
        refs = item.get("references", [])
        if not isinstance(refs, list) or any(not isinstance(x, str) or len(x) > 200 for x in refs):
            raise ValueError("Invalid diagram references")
        normalized.append({"title": field(item, "title", limit=200),
                           "description": field(item, "description", ""),
                           "source": field(item, "source"),
                           "references": refs})
    return {"title": field(spec, "title", limit=200),
            "summary": field(spec, "summary", ""), "phase": phase,
            "status": "DRAFT", "pele_version": PELE_VERSION,
            "sources": fingerprint(project, spec.get("sources", [])),
            "diagrams": normalized}


def evidence_path(project, name):
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError("Invalid project-relative evidence path")
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.as_posix() != name:
        raise ValueError("Evidence path must be canonical and inside project")
    if any(part.startswith(".") and part != ".ba" for part in path.parts):
        raise ValueError("Hidden evidence paths are excluded except .ba/")
    if any(part.lower() in {"node_modules", "vendor", "secrets", "credentials", "ba-workspace.html"} for part in path.parts):
        raise ValueError("Excluded evidence path")
    if path.suffix.lower() in {".pem", ".key", ".p12", ".pfx", ".kdbx"}:
        raise ValueError("Excluded credential file")
    resolved = (project / path).resolve()
    if resolved != project / path or not resolved.is_relative_to(project) or not resolved.is_file():
        raise ValueError("Evidence file missing, symlinked or outside project: " + name)
    if resolved.stat().st_size > 10_000_000:
        raise ValueError("Evidence file exceeds fingerprint size limit")
    return resolved


def evidence_fingerprints(project, names):
    return [{"path": n, "sha256": digest(evidence_path(project, n).read_bytes())}
            for n in sorted(set(names))]


def strings(obj, key, limit=2000, count=40):
    value = obj.get(key, [])
    if not isinstance(value, list) or len(value) > count or any(
        not isinstance(x, str) or not x.strip() or len(x) > limit for x in value
    ):
        raise ValueError("Invalid list: " + key)
    return value


def required_text(obj, key, limit=2000):
    value = field(obj, key, limit=limit)
    if not value.strip():
        raise ValueError("Empty field: " + key)
    return value


def view_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", value):
        raise ValueError("Invalid visual_id")
    return value


def normalize_view(project, item, phase):
    if not isinstance(item, dict):
        raise ValueError("Visual must be an object")
    intent = required_text(item, "intent", 50)
    kind = required_text(item, "kind", 50)
    choice = MATRIX.get(intent)
    if not choice or choice["kind"] != kind or kind in {"text", "wireframe"}:
        raise ValueError("Visual kind does not match a supported intent; use text when deferred")
    status = required_text(item, "status", 30)
    level = required_text(item, "level", 5)
    if status not in STATUSES or level not in {"L0", "L1", "L2"}:
        raise ValueError("Invalid evidence status or detail level")
    refs = strings(item, "references", limit=200)
    names = strings(item, "source_paths", limit=500, count=100)
    if status in {"OBSERVED", "APPROVED"} and (not refs or not names):
        raise ValueError("Observed/approved views need references and source paths")
    if any(n.startswith(".ba/changes/") for n in names) or any(re.search(r"\bCHG-\d+\b", r) for r in refs):
        if status != "PROPOSED":
            raise ValueError("Change-linked views must be marked PROPOSED in Phase 02")
    if status == "APPROVED":
        approved = False
        brain = evidence_path(project, ".ba/PROJECT.md").read_text(encoding="utf-8")
        baseline = re.search(r"(?ms)^## Current Baselines\s*\n(.*?)(?=^## |\Z)", brain)
        current = baseline.group(1) if baseline else ""
        for n in names:
            if re.fullmatch(r"\.ba/phases/[^/]+/R\d+\.md", n):
                content = evidence_path(project, n).read_text(encoding="utf-8")
                if (re.search(r"(?m)^\*\*Status:\*\* APPROVED(?:_WITH_OPEN_ITEMS)?\s*$", content)
                        and "## Approval" in content and "Approval scope" in content
                        and re.search(r"(?<![\w./-])" + re.escape(n) + r"(?![\w./-])", current)):
                    approved = True
        if not approved or not any(n in {".ba/PROJECT.md", ".ba/REQUIREMENTS.md", ".ba/DECISIONS.md"} for n in names):
            raise ValueError("Approved view needs a current approved baseline and canonical source")
    # Canonical context changes invalidate referenced views conservatively.
    if names:
        names = list(set(names) | {n for n in (".ba/PROJECT.md", ".ba/REQUIREMENTS.md", ".ba/DECISIONS.md") if (project / n).is_file()})
    data = {"visual_id": view_id(item.get("visual_id")), "title": required_text(item, "title", 200),
            "description": field(item, "description", ""), "phase": phase,
            "question": required_text(item, "question"), "intent": intent, "kind": kind,
            "tab": choice["tab"], "selection_reason": required_text(item, "selection_reason"),
            "status": status, "level": level, "references": refs,
            "sources": evidence_fingerprints(project, names),
            "open_questions": strings(item, "open_questions"),
            "change_summary": field(item, "change_summary", ""), "stale": False}
    if kind in TABLE_KINDS:
        columns = strings(item, "columns", limit=200, count=12)
        rows = item.get("rows")
        if not columns or not isinstance(rows, list) or not rows or len(rows) > 100:
            raise ValueError("Table requires columns and rows")
        if any(not isinstance(row, list) or len(row) != len(columns) or
               any(not isinstance(cell, str) or len(cell) > 2000 for cell in row) for row in rows):
            raise ValueError("Invalid table row")
        data.update(columns=columns, rows=rows)
    else:
        source = required_text(item, "source", MAX_SOURCE)
        if not re.match(PREFIXES[kind], source.lstrip()):
            raise ValueError("Mermaid syntax does not match selected visual kind")
        data["source"] = source
    return data


def stale_view(project, item):
    try:
        return evidence_fingerprints(project, [s["path"] for s in item["sources"]]) != item["sources"]
    except (OSError, ValueError, KeyError, TypeError):
        return True


def normalize_v2(project, spec, previous=None):
    phase = required_text(spec, "phase", 30)
    if phase not in {"UNDERSTAND", "REQUIREMENTS", "DESIGN"}:
        raise ValueError("Phase 02 supports Understand, Requirements and Design")
    items = spec.get("visuals")
    if not isinstance(items, list) or not items or len(items) > MAX_DIAGRAMS:
        raise ValueError("At least one visual required; use text otherwise")
    updated = [normalize_view(project, item, phase) for item in items]
    ids = [v["visual_id"] for v in updated]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate visual_id")
    removed = {view_id(x) for x in strings(spec, "remove_ids", limit=64)}
    if removed.intersection(ids):
        raise ValueError("Cannot remove and update the same visual")
    focus = view_id(spec.get("focus_id"))
    if focus not in ids:
        raise ValueError("Current focus must be a newly reviewed visual")
    merged = []
    if previous is not None:
        if previous.get("schema_version") != 2:
            raise ValueError("Incremental updates require a v2 workspace")
        for old in previous["diagrams"]:
            if old["visual_id"] in removed or old["visual_id"] in ids:
                continue
            old = dict(old)
            old["retained"] = True
            old["stale"] = bool(old.get("stale") or stale_view(project, old) or old["phase"] != phase or not old["sources"])
            merged.append(old)
    merged.extend(updated)
    if len(merged) > MAX_DIAGRAMS:
        raise ValueError("Workspace exceeds visual limit; remove obsolete views explicitly")
    return {"schema_version": 2, "title": required_text(spec, "title", 200),
            "summary": field(spec, "summary", ""), "phase": phase, "focus_id": focus,
            "status": "DRAFT", "pele_version": PELE_VERSION,
            "sources": [], "diagrams": merged}


def script_hash(script):
    return "'sha256-" + base64.b64encode(hashlib.sha256(script.encode()).digest()).decode() + "'"


def safe_script(script):
    if re.search(r"</script|<!--", script, re.I):
        raise ValueError("Inline script contains unsafe HTML script delimiters")
    return script


def assemble(data, bundle, license_text, template, runtime):
    bundle, runtime = safe_script(bundle), safe_script(runtime)
    payload = json.dumps(data, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    payload = payload.replace("<", r"\u003c").replace(">", r"\u003e").replace("&", r"\u0026")
    slots = {"DATA": payload, "PELE": bundle, "LICENSE": html.escape(license_text),
             "WORKSPACE_JS": runtime,
             "SCRIPT_HASHES": script_hash(bundle) + " " + script_hash(runtime)}
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: slots[m.group(1)], template)


def output_path(project):
    path = project / "docs" / "BA-Workspace.html"
    if path.parent.is_symlink() or path.is_symlink() or path.resolve() != path:
        raise ValueError("Output path escapes project or is a symlink")
    return path


def read_generated(path):
    content = path.read_text(encoding="utf-8")
    if MARKER not in content:
        raise ValueError("Not a generated BA workspace")
    match = DATA_RE.search(content)
    if not match:
        raise ValueError("Missing workspace metadata")
    return json.loads(match.group(1))


def generate(project, input_path, update=False):
    if input_path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("Workspace input exceeds size limit")
    spec = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        raise ValueError("Input must be an object")
    out = output_path(project)
    previous = read_generated(out) if out.exists() else None
    if update and (previous is None or spec.get("schema_version") != 2):
        raise ValueError("--update requires an existing workspace and v2 input")
    if spec.get("schema_version", 1) not in {1, 2}:
        raise ValueError("Unsupported input schema")
    data = normalize_v2(project, spec, previous if update else None) if spec.get("schema_version") == 2 else normalize(project, spec)
    package = ASSETS / "node_modules" / "pele"
    if not package.is_dir():
        raise ValueError("Pele is not prepared. Run npm install --prefix assets/visual --ignore-scripts --no-audit --no-fund from the plugin root.")
    manifest = json.loads((package / "package.json").read_text(encoding="utf-8"))
    if manifest.get("name") != "pele" or manifest.get("version") != PELE_VERSION:
        raise ValueError("Installed Pele version does not match pinned version")
    result = assemble(data, (package / "dist" / "pele.global.js").read_text(encoding="utf-8"),
                      (package / "LICENSE").read_text(encoding="utf-8"),
                      (ASSETS / "workspace-template.html").read_text(encoding="utf-8"),
                      (ASSETS / "workspace.js").read_text(encoding="utf-8"))
    out = output_path(project)
    if out.exists():
        read_generated(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Replace via an adjacent temporary file, so an interrupted write cannot truncate the old workspace.
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=out.parent, delete=False) as temp:
        temporary = Path(temp.name)
        try:
            temp.write(result)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(out)
    finally:
        temporary.unlink(missing_ok=True)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--input", type=Path, help="Draft visual JSON input")
    mode.add_argument("--check", action="store_true", help="Check declared source fingerprints")
    parser.add_argument("--update", action="store_true", help="Merge v2 views by stable ID")
    args = parser.parse_args(argv)
    project = args.project.resolve()
    try:
        if not project.is_dir():
            raise ValueError("Project directory does not exist")
        if args.check:
            data = read_generated(output_path(project))
            if data.get("schema_version") == 2:
                stale = [v["visual_id"] for v in data["diagrams"] if v.get("stale") or stale_view(project, v)]
                unverified = [v["visual_id"] for v in data["diagrams"] if not v["sources"]]
                if stale or unverified:
                    print("STALE: " + ", ".join(stale) + "; UNVERIFIABLE: " + ", ".join(unverified), file=sys.stderr)
                    return 1
                print("Declared view source fingerprints match; semantic completeness is not verified.")
                return 0
            sources = data["sources"]
            if not sources:
                print("UNVERIFIABLE: no project sources declared", file=sys.stderr)
                return 1
            if fingerprint(project, [s["path"] for s in sources]) != sources:
                print("STALE: declared source content changed", file=sys.stderr)
                return 1
            print("Declared source fingerprints match; semantic completeness is not verified.")
        else:
            print(generate(project, args.input, args.update))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("BA visual: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
