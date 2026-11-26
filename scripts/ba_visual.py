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


def generate(project, input_path):
    if input_path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("Workspace input exceeds size limit")
    data = normalize(project, json.loads(input_path.read_text(encoding="utf-8")))
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
    args = parser.parse_args(argv)
    project = args.project.resolve()
    try:
        if not project.is_dir():
            raise ValueError("Project directory does not exist")
        if args.check:
            data = read_generated(output_path(project))
            sources = data["sources"]
            if not sources:
                print("UNVERIFIABLE: no project sources declared", file=sys.stderr)
                return 1
            if fingerprint(project, [s["path"] for s in sources]) != sources:
                print("STALE: declared source content changed", file=sys.stderr)
                return 1
            print("Declared source fingerprints match; semantic completeness is not verified.")
        else:
            print(generate(project, args.input))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("BA visual: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
