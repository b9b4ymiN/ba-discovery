import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.ba_eval import evaluate_run


def test_visual_selection_fixtures(tmp_path):
    for scenario in sorted((ROOT / "evals/scenarios").glob("V*")):
        expected = json.loads((scenario / "expectations.json").read_text())["expectations"][0]["params"]["kind"]
        for actual in (expected, "flowchart" if expected != "flowchart" else "sequence"):
            events = [{"type": "ASSISTANT", "operation": "visual_selection", "visual_kind": actual}]
            if actual != "text":
                events.append({"type": "STATE_WRITE", "target": "docs/BA-Workspace.html"})
            run = {"scenario_id": scenario.name, "runtime": "synthetic-fixture",
                   "telemetry": {"events_complete": True}, "events": events}
            path = tmp_path / "run.json"
            path.write_text(json.dumps(run))
            result = evaluate_run(scenario, path, None)
            assert result["criteria"][0]["status"] == ("PASS" if actual == expected else "FAIL")
            assert result["criteria"][1]["status"] == "NOT_OBSERVED"
            run["telemetry"]["events_complete"] = False
            path.write_text(json.dumps(run))
            assert evaluate_run(scenario, path, None)["criteria"][0]["status"] == "NOT_OBSERVED"
