import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ba_visual", ROOT / "scripts" / "ba_visual.py")
visual = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(visual)


class TestVisualFoundation(unittest.TestCase):
    def test_source_fingerprint_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            brain = project / ".ba"
            brain.mkdir()
            record = brain / "PROJECT.md"
            record.write_text("original")
            before = visual.fingerprint(project, [".ba/PROJECT.md"])
            record.write_text("changed")
            self.assertNotEqual(before, visual.fingerprint(project, [".ba/PROJECT.md"]))
            with self.assertRaises(ValueError):
                visual.fingerprint(project, [".ba/../outside"])

    def test_draft_status_and_safe_embedding(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            payload = {"title": "</script><script>alert(1)</script>", "phase": "DESIGN",
                       "status": "APPROVED", "diagrams": []}
            data = visual.normalize(project, payload)
            self.assertEqual(data["status"], "DRAFT")
            template = (visual.ASSETS / "workspace-template.html").read_text()
            runtime = (visual.ASSETS / "workspace.js").read_text()
            page = visual.assemble(data, "window.pele={};", "MIT", template, runtime)
            self.assertNotIn(payload["title"], page)
            self.assertEqual(json.loads(visual.DATA_RE.search(page).group(1))["title"], payload["title"])
            self.assertIn("connect-src 'none'", page)
            self.assertIn(visual.script_hash(runtime), page)
            self.assertNotIn("<script src=", page)

    def test_reject_unsafe_bundle_delimiter(self):
        with self.assertRaises(ValueError):
            visual.safe_script("</SCRIPT>")

    def test_output_cannot_target_project_brain_via_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder).resolve()
            brain = project / ".ba"
            brain.mkdir()
            try:
                (project / "docs").symlink_to(brain, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaises(ValueError):
                visual.output_path(project)

    def test_unrelated_output_is_not_generated(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "BA-Workspace.html"
            path.write_text("<html>unrelated</html>")
            with self.assertRaises(ValueError):
                visual.read_generated(path)


if __name__ == "__main__":
    unittest.main()
