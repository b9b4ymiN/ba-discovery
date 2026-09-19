import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_behavior_contract_contains_stable_criterion_families_and_portability_rule():
    path = ROOT / "evals/behavior-contract.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    for criterion in [
        "SRC-01", "SRC-02", "SRC-03",
        "ANS-01", "ANS-02", "ANS-03", "ANS-04",
        "QST-01", "QST-02", "QST-03",
        "CLS-01", "CLS-02", "CLS-03",
        "PRO-01", "PRO-02",
        "APR-01", "APR-02",
        "RES-01", "RES-02", "RES-03",
    ]:
        assert criterion in text
    assert "must-pass" in text
    assert "diagnostic" in text
    assert "Core BA behavior and durable artifacts must remain vendor-neutral." in text
    assert "Platform-specific optimizations may exist only as optional adapters." in text


def test_run_record_schema_is_vendor_neutral_and_allows_missing_telemetry():
    schema = json.loads((ROOT / "evals/schema/run-record.schema.json").read_text(encoding="utf-8"))
    assert schema["required"] == ["scenario_id", "runtime", "events"]
    props = schema["properties"]
    assert props["runtime"]["type"] == "string"
    assert props["model"]["type"] == "string"
    event = props["events"]["items"]
    assert set(event["properties"]["type"]["enum"]) == {
        "USER", "ASSISTANT", "INSPECT", "RESEARCH", "STATE_WRITE", "APPROVAL"
    }
    assert "target" not in event["required"]
    assert "text" not in event["required"]


def test_expectations_schema_supports_criterion_level_evaluation():
    schema = json.loads((ROOT / "evals/schema/expectations.schema.json").read_text(encoding="utf-8"))
    item = schema["properties"]["expectations"]["items"]
    assert item["required"] == ["criterion", "level", "check", "params", "semantic_review"]
    assert set(item["properties"]["level"]["enum"]) == {"must-pass", "diagnostic"}
    assert item["properties"]["semantic_review"]["type"] == "boolean"


def test_five_required_scenario_packages_exist_with_contract_files():
    scenarios = ROOT / "evals/scenarios"
    expected = {
        "G01-greenfield-answerability",
        "B01-brownfield-source-gate",
        "X01-external-design-bypass",
        "U01-uncertain-estimate",
        "R01-resume",
    }
    found = {p.name for p in scenarios.iterdir() if p.is_dir()} if scenarios.exists() else set()
    assert expected <= found
    for name in expected:
        assert (scenarios / name / "SCENARIO.md").is_file()
        expectations = json.loads((scenarios / name / "expectations.json").read_text(encoding="utf-8"))
        assert expectations["scenario_id"] == name
        assert expectations["expectations"]


def test_brownfield_bypass_and_resume_scenarios_include_portable_seed_artifacts():
    required = [
        ROOT / "evals/scenarios/B01-brownfield-source-gate/seed/docs/current-workflow.md",
        ROOT / "evals/scenarios/X01-external-design-bypass/seed/docs/approved-requirements.md",
        ROOT / "evals/scenarios/R01-resume/seed/.ba/PROJECT.md",
        ROOT / "evals/scenarios/R01-resume/seed/.ba/REQUIREMENTS.md",
    ]
    for path in required:
        assert path.is_file(), path


def test_evals_readme_documents_manual_capture_and_optional_adapters():
    text = (ROOT / "evals/README.md").read_text(encoding="utf-8")
    for phrase in [
        "Manual capture",
        "Optional adapters",
        "No vendor-specific feature is required for BA Discovery correctness.",
        "PASS",
        "FAIL",
        "NOT_OBSERVED",
        "NOT_APPLICABLE",
    ]:
        assert phrase in text


def test_v08_behavior_contract_adds_change_management_families():
    text = (ROOT / "evals/behavior-contract.md").read_text(encoding="utf-8")
    for criterion in [
        "CHG-01", "CHG-02", "CHG-03", "CHG-04", "CHG-05",
        "IMP-01", "IMP-02",
        "CTX-01",
        "DEP-01",
        "USR-01",
        "CMT-01", "CMT-02",
        "RES-04",
    ]:
        assert criterion in text


def test_run_record_schema_supports_scoped_approval_without_vendor_fields():
    schema = json.loads((ROOT / "evals/schema/run-record.schema.json").read_text(encoding="utf-8"))
    event = schema["properties"]["events"]["items"]
    assert set(event["properties"]["scope"]["enum"]) == {"PHASE", "IMPACT", "FINAL"}
    assert "scope" not in event["required"]


def test_ten_v08_change_scenarios_exist():
    scenarios = ROOT / "evals/scenarios"
    expected = {
        "CM01-extend-existing-change",
        "CM02-new-business-concern",
        "CM03-uncertain-change-identity",
        "CM04-pending-truth-leakage",
        "CM05-minimum-revalidation",
        "CM06-history-not-ambient",
        "CM07-provisional-dependency",
        "CM08-single-user-guard",
        "CM09-post-commit-verification",
        "CM10-change-resume",
    }
    found = {p.name for p in scenarios.iterdir() if p.is_dir()}
    assert expected <= found
    for name in expected:
        assert (scenarios / name / "SCENARIO.md").is_file()
        payload = json.loads((scenarios / name / "expectations.json").read_text(encoding="utf-8"))
        assert payload["scenario_id"] == name
        assert payload["expectations"]
