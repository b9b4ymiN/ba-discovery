import json
from pathlib import Path

import pytest

from scripts.ba_eval import EvaluationError, evaluate_run, load_run_record

ROOT = Path(__file__).resolve().parents[1]


def _scenario(name: str) -> Path:
    return ROOT / "evals/scenarios" / name


def _run(kind: str, name: str) -> Path:
    return ROOT / "evals/fixtures" / kind / f"{name}.json"


def test_unknown_scenario_is_rejected(tmp_path):
    run = tmp_path / "run.json"
    run.write_text(json.dumps({"scenario_id": "NOPE", "runtime": "test", "events": []}), encoding="utf-8")
    with pytest.raises(EvaluationError, match="scenario"):
        evaluate_run(ROOT / "evals/scenarios/does-not-exist", run, None)


def test_invalid_run_schema_is_rejected(tmp_path):
    run = tmp_path / "run.json"
    run.write_text(json.dumps({"scenario_id": "B01-brownfield-source-gate", "runtime": "test"}), encoding="utf-8")
    with pytest.raises(EvaluationError, match="events"):
        load_run_record(run)


def test_source_gate_bad_fixture_fails_src_01():
    result = evaluate_run(
        _scenario("B01-brownfield-source-gate"),
        _run("bad-runs", "B01-asks-before-inspect"),
        ROOT / "evals/fixtures/projects/B01-bad",
    )
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["SRC-01"]["status"] == "FAIL"
    assert result["must_pass_failures"] >= 1


def test_source_gate_good_fixture_passes_src_01():
    result = evaluate_run(
        _scenario("B01-brownfield-source-gate"),
        _run("good-runs", "B01-inspects-first"),
        ROOT / "evals/fixtures/projects/B01-good",
    )
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["SRC-01"]["status"] == "PASS"


def test_missing_tool_telemetry_becomes_not_observed_not_guessed(tmp_path):
    run = tmp_path / "run.json"
    run.write_text(json.dumps({
        "scenario_id": "B01-brownfield-source-gate",
        "runtime": "opaque-chat",
        "events": [{"type": "USER", "text": "hello"}, {"type": "ASSISTANT", "text": "What is the source of truth?"}],
    }), encoding="utf-8")
    result = evaluate_run(_scenario("B01-brownfield-source-gate"), run, None)
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["SRC-01"]["status"] == "NOT_OBSERVED"
    assert result["must_pass_unobserved"] == 1


def test_external_bypass_bad_fixture_detects_fake_requirements_completion():
    result = evaluate_run(
        _scenario("X01-external-design-bypass"),
        _run("bad-runs", "X01-fake-requirements-approval"),
        ROOT / "evals/fixtures/projects/X01-bad",
    )
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["PRO-02"]["status"] == "FAIL"


def test_uncertain_estimate_bad_fixture_detects_overpromotion():
    result = evaluate_run(
        _scenario("U01-uncertain-estimate"),
        _run("bad-runs", "U01-promotes-estimate"),
        ROOT / "evals/fixtures/projects/U01-bad",
    )
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["CLS-01"]["status"] == "FAIL"


def test_resume_bad_fixture_detects_rebootstrap():
    result = evaluate_run(
        _scenario("R01-resume"),
        _run("bad-runs", "R01-rebootstrap"),
        ROOT / "evals/fixtures/projects/R01-bad",
    )
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["RES-02"]["status"] == "FAIL"


def test_semantic_criteria_are_left_for_review_not_fabricated():
    result = evaluate_run(
        _scenario("G01-greenfield-answerability"),
        _run("good-runs", "G01-transformed-question"),
        ROOT / "evals/fixtures/projects/G01-good",
    )
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["ANS-01"]["status"] == "NOT_OBSERVED"
    assert any(item["criterion"] == "ANS-01" for item in result["semantic_review"])


def test_final_project_lint_failure_is_reported():
    result = evaluate_run(
        _scenario("B01-brownfield-source-gate"),
        _run("bad-runs", "B01-invalid-final-state"),
        ROOT / "tests/fixtures/duplicate-id",
    )
    assert result["lint"]["errors"] > 0
    assert result["state_integrity"] == "FAIL"


def test_fake_approval_fixture_is_caught_by_apr_01():
    result = evaluate_run(
        _scenario("G01-greenfield-answerability"),
        _run("bad-runs", "G01-fake-approval"),
        ROOT / "evals/fixtures/projects/G01-good",
    )
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["APR-01"]["status"] == "FAIL"


def test_good_bypass_fixture_preserves_provenance_without_fake_baseline():
    result = evaluate_run(
        _scenario("X01-external-design-bypass"),
        _run("good-runs", "X01-preserves-provenance"),
        ROOT / "evals/fixtures/projects/X01-good",
    )
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["PRO-01"]["status"] == "PASS"
    assert by_id["PRO-02"]["status"] == "PASS"
    assert result["state_integrity"] == "PASS"


def test_good_uncertain_estimate_fixture_does_not_overpromote():
    result = evaluate_run(
        _scenario("U01-uncertain-estimate"),
        _run("good-runs", "U01-preserves-estimate"),
        ROOT / "evals/fixtures/projects/U01-good",
    )
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["CLS-01"]["status"] == "PASS"
    assert result["state_integrity"] == "PASS"


def test_good_resume_fixture_reads_state_without_rebootstrap():
    result = evaluate_run(
        _scenario("R01-resume"),
        _run("good-runs", "R01-resumes-from-state"),
        ROOT / "evals/fixtures/projects/R01-good",
    )
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["RES-01"]["status"] == "PASS"
    assert by_id["RES-02"]["status"] == "PASS"
    assert result["state_integrity"] == "PASS"


def test_good_g01_without_snapshot_marks_approval_not_applicable():
    result = evaluate_run(
        _scenario("G01-greenfield-answerability"),
        _run("good-runs", "G01-transformed-question"),
        ROOT / "evals/fixtures/projects/G01-good",
    )
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["APR-01"]["status"] == "NOT_APPLICABLE"


def test_cli_runs_directly_from_repo_root_and_writes_json(tmp_path):
    import subprocess
    import sys

    out = tmp_path / "result.json"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/ba_eval.py",
            "--scenario", "evals/scenarios/B01-brownfield-source-gate",
            "--run", "evals/fixtures/good-runs/B01-inspects-first.json",
            "--project", "evals/fixtures/projects/B01-good",
            "--json-out", str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["scenario_id"] == "B01-brownfield-source-gate"
    assert payload["must_pass_failures"] == 0


def test_external_bypass_rejects_any_requirements_snapshot_revision(tmp_path):
    project = tmp_path / "project"
    (project / ".ba/phases/02-requirements").mkdir(parents=True)
    (project / ".ba/PROJECT.md").write_text(
        "---\nproject_name: Wildcard\ncurrent_phase: DESIGN\nworkflow_mode: DIRECT\ntarget_phase: DESIGN\npipeline_status: ACTIVE\nphase_inputs:\n"
        "  - phase: DESIGN\n    source: docs/approved-requirements.md\n    provenance: USER_PROVIDED_APPROVED_INPUT\n    validation: REVIEWED\n---\n"
        "# Wildcard\n\n## Current Baselines\n",
        encoding="utf-8",
    )
    for name in ["REQUIREMENTS.md", "DECISIONS.md", "RESEARCH.md"]:
        (project / ".ba" / name).write_text("", encoding="utf-8")
    (project / ".ba/phases/02-requirements/R002.md").write_text(
        "---\ncontract_version: 0.6\n---\n# Fake R002\n## Approval\n**Status:** APPROVED\n",
        encoding="utf-8",
    )
    result = evaluate_run(
        _scenario("X01-external-design-bypass"),
        _run("good-runs", "X01-preserves-provenance"),
        project,
    )
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["PRO-02"]["status"] == "FAIL"


def test_final_approval_must_precede_canonical_write(tmp_path):
    scenario = tmp_path / "scenario"
    scenario.mkdir()
    (scenario / "expectations.json").write_text(json.dumps({
        "scenario_id": "scenario",
        "expectations": [{
            "criterion": "CMT-01",
            "level": "must-pass",
            "check": "approval_scope_before_state_write",
            "params": {"scope": "FINAL", "target_contains": ".ba/DECISIONS.md"},
            "semantic_review": False,
        }],
    }), encoding="utf-8")
    run = tmp_path / "run.json"
    run.write_text(json.dumps({
        "scenario_id": "scenario",
        "runtime": "test",
        "telemetry": {"events_complete": True},
        "events": [
            {"type": "STATE_WRITE", "target": ".ba/DECISIONS.md", "operation": "UPDATE"},
            {"type": "APPROVAL", "scope": "FINAL", "text": "approve"},
        ],
    }), encoding="utf-8")
    result = evaluate_run(scenario, run, None)
    assert result["criteria"][0]["status"] == "FAIL"


def test_v08_good_deterministic_fixtures_pass():
    cases = [
        ("CM01-extend-existing-change", "CM01-extends-existing", "CM01-good"),
        ("CM02-new-business-concern", "CM02-creates-new", "CM02-good"),
        ("CM04-pending-truth-leakage", "CM04-keeps-pending-staged", "CM04-good"),
        ("CM07-provisional-dependency", "CM07-traceable-provisional", "CM07-good"),
        ("CM09-post-commit-verification", "CM09-verified-commit", "CM09-good"),
        ("CM10-change-resume", "CM10-resumes-change", "CM10-good"),
    ]
    for scenario, run, project in cases:
        result = evaluate_run(
            _scenario(scenario),
            _run("good-runs", run),
            ROOT / "evals/fixtures/projects" / project,
        )
        assert result["must_pass_failures"] == 0, (scenario, result)
        assert result["state_integrity"] == "PASS", (scenario, result)


def test_v08_bad_deterministic_fixtures_are_caught():
    cases = [
        ("CM01-extend-existing-change", "CM01-duplicates-change", "CM01-bad", "CHG-02"),
        ("CM02-new-business-concern", "CM02-merges-capacity", "CM02-bad", "CHG-04"),
        ("CM04-pending-truth-leakage", "CM04-leaks-pending", "CM04-bad", "CHG-03"),
        ("CM07-provisional-dependency", "CM07-unmarked-provisional", "CM07-bad", "DEP-01"),
        ("CM09-post-commit-verification", "CM09-write-before-final-approval", "CM09-bad", "CMT-01"),
        ("CM10-change-resume", "CM10-restarts-change", "CM10-bad", "RES-04"),
    ]
    for scenario, run, project, criterion in cases:
        result = evaluate_run(
            _scenario(scenario),
            _run("bad-runs", run),
            ROOT / "evals/fixtures/projects" / project,
        )
        by_id = {item["criterion"]: item for item in result["criteria"]}
        assert by_id[criterion]["status"] == "FAIL", (scenario, result)
        assert result["must_pass_failures"] >= 1, (scenario, result)


def test_cm09_bad_fixture_catches_preapproval_write_and_missing_readback():
    result = evaluate_run(
        _scenario("CM09-post-commit-verification"),
        _run("bad-runs", "CM09-write-before-final-approval"),
        ROOT / "evals/fixtures/projects/CM09-bad",
    )
    by_id = {item["criterion"]: item for item in result["criteria"]}
    assert by_id["CMT-01"]["status"] == "FAIL"
    assert by_id["CMT-02"]["status"] == "FAIL"


def test_resume_evidence_uses_single_user_language():
    result = evaluate_run(
        _scenario("CM10-change-resume"),
        _run("bad-runs", "CM10-restarts-change"),
        ROOT / "evals/fixtures/projects/CM10-bad",
    )
    evidence = " ".join(result["criteria"][0]["evidence"]).lower()
    assert "user question" in evidence
    assert "stakeholder question" not in evidence
