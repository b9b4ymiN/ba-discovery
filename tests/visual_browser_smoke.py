"""Explicit browser integration test; not part of standard-library tooling."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "ba_visual.py"
EXAMPLE = ROOT / "examples" / "order-allocation-planner"


def run(*args, expected=0):
    result = subprocess.run([sys.executable, str(CLI), *map(str, args)],
                            capture_output=True, text=True)
    assert result.returncode == expected, result.stdout + result.stderr
    return result


def snapshot(brain):
    return {str(p.relative_to(brain)): p.read_bytes()
            for p in brain.rglob("*") if p.is_file()}


def main():
    with tempfile.TemporaryDirectory() as folder:
        project = Path(folder) / "project"
        shutil.copytree(EXAMPLE, project)
        brain = project / ".ba"
        before = snapshot(brain)
        title = "ทดสอบ </script><script>window.injected=true</script>"
        samples = [
            ("Flow", 'flowchart LR\nA["รับคำสั่งซื้อ"] --> B["ตรวจสอบ"]'),
            ("Sequence", "sequenceDiagram\nparticipant A\nparticipant B\nA->>B: Request"),
            ("ER", "erDiagram\nORDER ||--o{ LINE : contains"),
            ("State", "stateDiagram-v2\n[*] --> Ready\nReady --> [*]"),
            ("Architecture", "architecture-beta\nservice api(server)[API]\nservice db(database)[DB]\napi:R -- L:db"),
            ("Invalid", "this is not a diagram"),
        ]
        spec = {"title": title, "phase": "DESIGN", "summary": "Illustrative only",
                "sources": [".ba/PROJECT.md"],
                "diagrams": [{"title": label, "source": source, "references": []}
                             for label, source in samples]}
        input_file = Path(folder) / "visual.json"
        input_file.write_text(json.dumps(spec), encoding="utf-8")
        run("--project", project, "--input", input_file)
        run("--project", project, "--check")
        assert snapshot(brain) == before
        workspace = project / "docs" / "BA-Workspace.html"
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context(offline=True)
            page = context.new_page()
            remote = []
            errors = []
            page.on("request", lambda req: remote.append(req.url)
                    if req.url.startswith(("http://", "https://")) else None)
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.goto(workspace.as_uri(), wait_until="load")
            cards = page.locator("#diagrams article")
            assert cards.count() == len(samples), errors
            assert page.locator("#title").inner_text() == title
            assert page.evaluate("window.injected === undefined")
            assert "DRAFT / NOT AN APPROVAL" in page.locator(".notice").inner_text()
            for i, (label, source) in enumerate(samples[:-1]):
                card = cards.nth(i)
                img = card.locator("img")
                assert img.count() == 1, label + ": " + card.inner_text()
                assert img.evaluate("(img) => img.complete && img.naturalWidth > 0"), label
                assert card.locator(".error").count() == 0, label
                assert card.locator("pre").text_content() == source
            assert cards.last.locator(".error").count() == 1
            assert cards.last.locator("pre").text_content() == samples[-1][1]
            assert not errors, errors
            assert not remote, remote
            browser.close()
        assert snapshot(brain) == before
        record = brain / "PROJECT.md"
        record.write_bytes(record.read_bytes() + b"\n")
        run("--project", project, "--check", expected=1)
        print("Offline Chromium smoke test passed (five diagram types, invalid source, injection, freshness).")


if __name__ == "__main__":
    main()
