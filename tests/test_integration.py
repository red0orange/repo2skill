"""Tests for validation/integrate_data.py."""
import csv
import io
import math
import tempfile
import os
import pytest

from validation.integrate_data import (
    build_integrated_dataset,
    check_data_quality,
    load_github_metadata,
    load_skill_metrics,
    save_dataset,
    REQUIRED_COLUMNS,
)


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

SAMPLE_GITHUB_ITEM = {
    "repo_name": "example-owner/example-repo",
    "github_url": "https://github.com/example-owner/example-repo",
    "stars": 1562,
    "language": "JavaScript",
    "archived": False,
    "has_license": True,
    "license_name": "MIT",
    "task_clarity": 5,
    "interface_clarity": 5,
    "composability": 4,
    "automation_value": 5,
    "deployment_friction": 3,
    "operational_risk": 3,
    "skillability_core": 0.8,
    "opportunity_score": 0.76,
    "primary_capability": "web_automation",
    "granularity": "service_wrapper",
}

SAMPLE_GITHUB_ITEM_2 = {
    "repo_name": "another-owner/another-repo",
    "stars": 5000,
    "language": "Python",
    "archived": True,
    "has_license": False,
    "license_name": None,
    "task_clarity": 3,
    "interface_clarity": 3,
    "composability": 3,
    "automation_value": 3,
    "deployment_friction": 2,
    "operational_risk": 2,
    "skillability_core": 0.5,
    "opportunity_score": 0.40,
    "primary_capability": "data_processing",
    "granularity": "function_tool",
}

SAMPLE_CLAWHUB_ITEM = {
    "skill_id": "chef",
    "skill_name": "Chef",
    "stars": 2,
    "downloads": 666,
    "installs_all_time": 2,
    "versions": 1,
    "has_license": False,
    "is_popular": True,
    "log_downloads": 6.5,
    "task_clarity": 4,
    "interface_clarity": 4,
    "composability": 3,
    "automation_value": 4,
    "deployment_friction": 2,
    "operational_risk": 2,
    "skillability_core": 0.55,
    "opportunity_score": 0.33,
    "primary_capability": "knowledge_workflow_research",
    "granularity": "workflow_skill",
}

SAMPLE_CLAWHUB_ITEM_2 = {
    "skill_id": "my-tool",
    "skill_name": "My Tool",
    "stars": 100,
    "downloads": 5000,
    "installs_all_time": 300,
    "versions": 5,
    "has_license": True,
    "is_popular": True,
    "log_downloads": 8.5,
    "task_clarity": 5,
    "interface_clarity": 5,
    "composability": 5,
    "automation_value": 5,
    "deployment_friction": 1,
    "operational_risk": 1,
    "skillability_core": 0.95,
    "opportunity_score": 0.90,
    "primary_capability": "web_automation",
    "granularity": "service_wrapper",
}


# ---------------------------------------------------------------------------
# Test 1: Labels
# ---------------------------------------------------------------------------


def test_build_integrated_dataset_labels():
    """Clawhub items get label=1, GitHub items get label=0."""
    github_items = [SAMPLE_GITHUB_ITEM, SAMPLE_GITHUB_ITEM_2]
    clawhub_items = [SAMPLE_CLAWHUB_ITEM, SAMPLE_CLAWHUB_ITEM_2]

    dataset = build_integrated_dataset(github_items, clawhub_items)

    github_labels = [row["label"] for row in dataset if row["source"] == "github"]
    clawhub_labels = [row["label"] for row in dataset if row["source"] == "clawhub"]

    assert all(lbl == 0 for lbl in github_labels), "All GitHub items should have label=0"
    assert all(lbl == 1 for lbl in clawhub_labels), "All Clawhub items should have label=1"
    assert len(github_labels) == 2
    assert len(clawhub_labels) == 2


# ---------------------------------------------------------------------------
# Test 2: Columns
# ---------------------------------------------------------------------------


def test_build_integrated_dataset_columns():
    """All required columns are present in every row."""
    github_items = [SAMPLE_GITHUB_ITEM]
    clawhub_items = [SAMPLE_CLAWHUB_ITEM]

    dataset = build_integrated_dataset(github_items, clawhub_items)

    for row in dataset:
        for col in REQUIRED_COLUMNS:
            assert col in row, f"Missing column '{col}' in row with source={row.get('source')}"


def test_build_integrated_dataset_row_count():
    """Output has exactly len(github) + len(clawhub) rows."""
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM, SAMPLE_GITHUB_ITEM_2], [SAMPLE_CLAWHUB_ITEM])
    assert len(dataset) == 3


def test_build_integrated_dataset_empty_inputs():
    """Empty inputs produce an empty dataset without errors."""
    dataset = build_integrated_dataset([], [])
    assert dataset == []


def test_build_integrated_dataset_only_github():
    """Only GitHub items produce rows with label=0 and all columns."""
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM], [])
    assert len(dataset) == 1
    assert dataset[0]["label"] == 0
    for col in REQUIRED_COLUMNS:
        assert col in dataset[0]


def test_build_integrated_dataset_only_clawhub():
    """Only Clawhub items produce rows with label=1 and all columns."""
    dataset = build_integrated_dataset([], [SAMPLE_CLAWHUB_ITEM])
    assert len(dataset) == 1
    assert dataset[0]["label"] == 1
    for col in REQUIRED_COLUMNS:
        assert col in dataset[0]


# ---------------------------------------------------------------------------
# Test 3: Clawhub items have marketplace stats
# ---------------------------------------------------------------------------


def test_clawhub_items_have_marketplace_stats():
    """Clawhub items have clawhub_downloads, clawhub_installs, clawhub_versions, clawhub_stars."""
    dataset = build_integrated_dataset([], [SAMPLE_CLAWHUB_ITEM])
    row = dataset[0]

    assert row["clawhub_stars"] == SAMPLE_CLAWHUB_ITEM["stars"]
    assert row["clawhub_downloads"] == SAMPLE_CLAWHUB_ITEM["downloads"]
    assert row["clawhub_installs"] == SAMPLE_CLAWHUB_ITEM["installs_all_time"]
    assert row["clawhub_versions"] == SAMPLE_CLAWHUB_ITEM["versions"]


def test_clawhub_items_have_zero_github_stars():
    """Clawhub items have github_stars=0 (not NaN)."""
    dataset = build_integrated_dataset([], [SAMPLE_CLAWHUB_ITEM])
    row = dataset[0]
    assert row["github_stars"] == 0


def test_clawhub_items_not_archived():
    """Clawhub items always have archived=False."""
    dataset = build_integrated_dataset([], [SAMPLE_CLAWHUB_ITEM, SAMPLE_CLAWHUB_ITEM_2])
    for row in dataset:
        if row["source"] == "clawhub":
            assert row["archived"] is False


def test_clawhub_items_name_from_skill_name():
    """Clawhub items use skill_name as the display name."""
    dataset = build_integrated_dataset([], [SAMPLE_CLAWHUB_ITEM])
    row = dataset[0]
    assert row["name"] == "Chef"


# ---------------------------------------------------------------------------
# Test 4: GitHub items have no marketplace stats (NaN/None for clawhub_*)
# ---------------------------------------------------------------------------


def test_github_items_have_no_marketplace_stats():
    """GitHub items have NaN for all clawhub_* columns."""
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM], [])
    row = dataset[0]

    for col in ("clawhub_stars", "clawhub_downloads", "clawhub_installs", "clawhub_versions"):
        val = row[col]
        assert val is None or (isinstance(val, float) and math.isnan(val)), (
            f"Expected NaN/None for {col} in GitHub row, got {val!r}"
        )


def test_github_items_have_actual_github_stars():
    """GitHub items have the actual repo star count in github_stars."""
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM], [])
    row = dataset[0]
    assert row["github_stars"] == SAMPLE_GITHUB_ITEM["stars"]


def test_github_items_preserve_language():
    """GitHub items preserve the language field."""
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM], [])
    row = dataset[0]
    assert row["language"] == SAMPLE_GITHUB_ITEM["language"]


def test_github_items_preserve_archived():
    """GitHub items preserve the archived flag."""
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM_2], [])
    row = dataset[0]
    assert row["archived"] == SAMPLE_GITHUB_ITEM_2["archived"]


def test_github_items_name_from_repo_name():
    """GitHub items use repo_name as the name."""
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM], [])
    row = dataset[0]
    assert row["name"] == SAMPLE_GITHUB_ITEM["repo_name"]


# ---------------------------------------------------------------------------
# Test 5: check_data_quality returns required keys
# ---------------------------------------------------------------------------


def test_check_data_quality_returns_required_keys():
    """Quality check result has all expected top-level keys."""
    github_items = [SAMPLE_GITHUB_ITEM]
    clawhub_items = [SAMPLE_CLAWHUB_ITEM]
    dataset = build_integrated_dataset(github_items, clawhub_items)

    report = check_data_quality(dataset)

    required_keys = {
        "total_rows",
        "class_counts",
        "class_balance_ratio",
        "missing_rates",
        "skillability_by_class",
    }
    for key in required_keys:
        assert key in report, f"Quality report missing key: {key}"


def test_check_data_quality_total_rows():
    """Quality report total_rows matches dataset length."""
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM, SAMPLE_GITHUB_ITEM_2], [SAMPLE_CLAWHUB_ITEM])
    report = check_data_quality(dataset)
    assert report["total_rows"] == 3


def test_check_data_quality_class_counts():
    """Quality report class_counts correctly counts each label."""
    dataset = build_integrated_dataset(
        [SAMPLE_GITHUB_ITEM, SAMPLE_GITHUB_ITEM_2],
        [SAMPLE_CLAWHUB_ITEM, SAMPLE_CLAWHUB_ITEM_2],
    )
    report = check_data_quality(dataset)
    assert report["class_counts"][0] == 2   # GitHub
    assert report["class_counts"][1] == 2   # Clawhub


def test_check_data_quality_balance_ratio():
    """Quality report class_balance_ratio is Clawhub count / GitHub count."""
    dataset = build_integrated_dataset(
        [SAMPLE_GITHUB_ITEM, SAMPLE_GITHUB_ITEM_2],  # 2 GitHub
        [SAMPLE_CLAWHUB_ITEM],                        # 1 Clawhub
    )
    report = check_data_quality(dataset)
    assert report["class_balance_ratio"] == pytest.approx(0.5)


def test_check_data_quality_missing_rates_keys():
    """Quality report missing_rates contains an entry for every required column."""
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM], [SAMPLE_CLAWHUB_ITEM])
    report = check_data_quality(dataset)
    for col in REQUIRED_COLUMNS:
        assert col in report["missing_rates"], f"missing_rates missing column: {col}"


def test_check_data_quality_missing_rates_clawhub_cols():
    """GitHub rows have NaN for clawhub_* columns, raising the missing rate."""
    # 1 GitHub row + 1 Clawhub row => clawhub_downloads missing for 1/2 rows
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM], [SAMPLE_CLAWHUB_ITEM])
    report = check_data_quality(dataset)
    # clawhub_downloads is NaN for the GitHub item, present for the Clawhub item
    assert report["missing_rates"]["clawhub_downloads"] == pytest.approx(0.5)


def test_check_data_quality_empty_dataset():
    """Empty dataset returns sensible defaults without errors."""
    report = check_data_quality([])
    assert report["total_rows"] == 0
    assert report["class_balance_ratio"] is None


def test_check_data_quality_skillability_by_class():
    """skillability_by_class has entries for both label 0 and 1."""
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM], [SAMPLE_CLAWHUB_ITEM])
    report = check_data_quality(dataset)
    assert 0 in report["skillability_by_class"]
    assert 1 in report["skillability_by_class"]


# ---------------------------------------------------------------------------
# Test: save_dataset writes valid CSV with empty strings for NaN
# ---------------------------------------------------------------------------


def test_save_dataset_writes_csv():
    """save_dataset produces a readable CSV with the correct number of rows."""
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM], [SAMPLE_CLAWHUB_ITEM])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        tmp_path = f.name

    try:
        save_dataset(dataset, tmp_path)

        with open(tmp_path, newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        assert len(reader) == 2
    finally:
        os.unlink(tmp_path)


def test_save_dataset_nan_becomes_empty_string():
    """NaN values in clawhub_* columns become empty strings in CSV output."""
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM], [])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        tmp_path = f.name

    try:
        save_dataset(dataset, tmp_path)

        with open(tmp_path, newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        github_row = reader[0]
        for col in ("clawhub_stars", "clawhub_downloads", "clawhub_installs", "clawhub_versions"):
            assert github_row[col] == "", (
                f"Expected empty string for {col}, got {github_row[col]!r}"
            )
    finally:
        os.unlink(tmp_path)


def test_save_dataset_column_headers():
    """CSV file header matches REQUIRED_COLUMNS exactly."""
    dataset = build_integrated_dataset([SAMPLE_GITHUB_ITEM], [SAMPLE_CLAWHUB_ITEM])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        tmp_path = f.name

    try:
        save_dataset(dataset, tmp_path)

        with open(tmp_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames

        assert list(headers) == REQUIRED_COLUMNS
    finally:
        os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Test: load_github_metadata handles both list and dict-wrapped formats
# ---------------------------------------------------------------------------


def test_load_github_metadata_list_format(tmp_path):
    """load_github_metadata handles a plain list JSON."""
    data = [SAMPLE_GITHUB_ITEM]
    p = tmp_path / "github.json"
    import json
    p.write_text(json.dumps(data))
    result = load_github_metadata(str(p))
    assert len(result) == 1
    assert result[0]["repo_name"] == SAMPLE_GITHUB_ITEM["repo_name"]


def test_load_github_metadata_dict_format(tmp_path):
    """load_github_metadata handles {'metadata': [...]} format."""
    data = {"metadata": [SAMPLE_GITHUB_ITEM], "stats": {}}
    p = tmp_path / "github.json"
    import json
    p.write_text(json.dumps(data))
    result = load_github_metadata(str(p))
    assert len(result) == 1


def test_load_skill_metrics_list_format(tmp_path):
    """load_skill_metrics handles a plain list JSON."""
    data = [SAMPLE_CLAWHUB_ITEM]
    p = tmp_path / "skills.json"
    import json
    p.write_text(json.dumps(data))
    result = load_skill_metrics(str(p))
    assert len(result) == 1
    assert result[0]["skill_id"] == SAMPLE_CLAWHUB_ITEM["skill_id"]


def test_load_skill_metrics_dict_format(tmp_path):
    """load_skill_metrics handles {'metrics': [...]} format."""
    data = {"metrics": [SAMPLE_CLAWHUB_ITEM], "stats": {}}
    p = tmp_path / "skills.json"
    import json
    p.write_text(json.dumps(data))
    result = load_skill_metrics(str(p))
    assert len(result) == 1
