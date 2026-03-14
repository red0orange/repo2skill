"""Merge GitHub metadata and Clawhub skill metrics into unified dataset."""
import json
import csv
import math
from pathlib import Path

# Use only stdlib (no pandas) to keep simple

REQUIRED_COLUMNS = [
    "label",
    "source",
    "name",
    "task_clarity",
    "interface_clarity",
    "composability",
    "automation_value",
    "deployment_friction",
    "operational_risk",
    "skillability_core",
    "opportunity_score",
    "github_stars",
    "has_license",
    "language",
    "archived",
    "primary_capability",
    "granularity",
    "clawhub_stars",
    "clawhub_downloads",
    "clawhub_installs",
    "clawhub_versions",
]


def load_github_metadata(path: str) -> list:
    """Load GitHub metadata from Task 3 output.

    The JSON file has shape: {"metadata": [...], "stats": {...}}.
    Returns the list of repo dicts.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    # Expected structure: {"metadata": [...], "stats": {...}}
    if "metadata" in data:
        return data["metadata"]

    # Fallback: try common keys
    for key in ("repos", "items", "data", "results"):
        if key in data and isinstance(data[key], list):
            return data[key]

    raise ValueError(f"Cannot find repo list in {path}. Top-level keys: {list(data.keys())}")


def load_skill_metrics(path: str) -> list:
    """Load Clawhub skill metrics from Task 4 output.

    The JSON file has shape: {"metrics": [...], "stats": {...}}.
    Returns the list of skill metric dicts.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    # Expected structure: {"metrics": [...], "stats": {...}}
    if "metrics" in data:
        return data["metrics"]

    # Fallback: try common keys
    for key in ("skills", "items", "data", "results"):
        if key in data and isinstance(data[key], list):
            return data[key]

    raise ValueError(f"Cannot find skills list in {path}. Top-level keys: {list(data.keys())}")


def build_integrated_dataset(github_items: list, clawhub_items: list) -> list:
    """Merge into unified list of dicts with all required columns.

    GitHub items: label=0, clawhub_stars=NaN, clawhub_downloads=NaN, etc.
    Clawhub items: label=1, github_stars=0, archived=False.

    Returns list of dicts with exactly the REQUIRED_COLUMNS fields.
    """
    dataset = []

    # Process GitHub repos (label=0)
    for repo in github_items:
        row = {
            "label": 0,
            "source": "github",
            "name": repo.get("repo_name", ""),
            "task_clarity": repo.get("task_clarity"),
            "interface_clarity": repo.get("interface_clarity"),
            "composability": repo.get("composability"),
            "automation_value": repo.get("automation_value"),
            "deployment_friction": repo.get("deployment_friction"),
            "operational_risk": repo.get("operational_risk"),
            "skillability_core": repo.get("skillability_core"),
            "opportunity_score": repo.get("opportunity_score"),
            "github_stars": repo.get("stars", 0),
            "has_license": repo.get("has_license"),
            "language": repo.get("language"),
            "archived": repo.get("archived", False),
            "primary_capability": repo.get("primary_capability"),
            "granularity": repo.get("granularity"),
            # Clawhub-specific columns are NaN for GitHub items
            "clawhub_stars": float("nan"),
            "clawhub_downloads": float("nan"),
            "clawhub_installs": float("nan"),
            "clawhub_versions": float("nan"),
        }
        dataset.append(row)

    # Process Clawhub skills (label=1)
    for skill in clawhub_items:
        row = {
            "label": 1,
            "source": "clawhub",
            "name": skill.get("skill_name", skill.get("skill_id", "")),
            "task_clarity": skill.get("task_clarity"),
            "interface_clarity": skill.get("interface_clarity"),
            "composability": skill.get("composability"),
            "automation_value": skill.get("automation_value"),
            "deployment_friction": skill.get("deployment_friction"),
            "operational_risk": skill.get("operational_risk"),
            "skillability_core": skill.get("skillability_core"),
            "opportunity_score": skill.get("opportunity_score"),
            # GitHub stars are 0 for Clawhub items (they exist on the marketplace, not GitHub)
            "github_stars": 0,
            "has_license": skill.get("has_license"),
            "language": None,        # Clawhub skills don't have a single primary language
            "archived": False,       # Clawhub items are active marketplace skills
            "primary_capability": skill.get("primary_capability"),
            "granularity": skill.get("granularity"),
            # Clawhub marketplace stats
            "clawhub_stars": skill.get("stars"),
            "clawhub_downloads": skill.get("downloads"),
            "clawhub_installs": skill.get("installs_all_time"),
            "clawhub_versions": skill.get("versions"),
        }
        dataset.append(row)

    return dataset


def check_data_quality(dataset: list) -> dict:
    """Check data quality.

    Checks:
    - Missing value rates per column
    - Class balance (Clawhub vs GitHub ratio)
    - Skillability score distribution by class

    Returns quality report dict.
    """
    if not dataset:
        return {
            "total_rows": 0,
            "class_counts": {},
            "class_balance_ratio": None,
            "missing_rates": {},
            "skillability_by_class": {},
        }

    total = len(dataset)

    # Class balance
    class_counts = {}
    for row in dataset:
        label = row["label"]
        class_counts[label] = class_counts.get(label, 0) + 1

    n_clawhub = class_counts.get(1, 0)
    n_github = class_counts.get(0, 0)
    balance_ratio = n_clawhub / n_github if n_github > 0 else None

    # Missing value rates per column
    missing_rates = {}
    for col in REQUIRED_COLUMNS:
        missing_count = 0
        for row in dataset:
            val = row.get(col)
            if val is None or (isinstance(val, float) and math.isnan(val)):
                missing_count += 1
        missing_rates[col] = missing_count / total

    # Skillability score distribution by class
    skillability_by_class = {}
    for label_val in [0, 1]:
        scores = []
        for row in dataset:
            if row["label"] == label_val:
                sc = row.get("skillability_core")
                if sc is not None and not (isinstance(sc, float) and math.isnan(sc)):
                    scores.append(float(sc))
        if scores:
            mean_sc = sum(scores) / len(scores)
            sorted_sc = sorted(scores)
            n = len(sorted_sc)
            median_sc = sorted_sc[n // 2] if n % 2 == 1 else (sorted_sc[n // 2 - 1] + sorted_sc[n // 2]) / 2.0
            skillability_by_class[label_val] = {
                "count": len(scores),
                "mean": round(mean_sc, 4),
                "median": round(median_sc, 4),
                "min": round(min(scores), 4),
                "max": round(max(scores), 4),
            }
        else:
            skillability_by_class[label_val] = {"count": 0}

    return {
        "total_rows": total,
        "class_counts": class_counts,
        "class_balance_ratio": balance_ratio,
        "missing_rates": missing_rates,
        "skillability_by_class": skillability_by_class,
    }


def _nan_to_empty(value) -> str:
    """Convert a value to its CSV string representation.

    NaN and None become empty string (so pandas reads them as NaN automatically).
    Booleans become 'True'/'False'.
    Everything else uses str().
    """
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value)


def save_dataset(dataset: list, output_path: str):
    """Save dataset to CSV using stdlib csv module.

    NaN values are written as empty strings so downstream pandas reads them as NaN.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=REQUIRED_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in dataset:
            csv_row = {col: _nan_to_empty(row.get(col)) for col in REQUIRED_COLUMNS}
            writer.writerow(csv_row)


def integrate_data(github_path: str, skill_metrics_path: str, output_path: str) -> dict:
    """Main integration function. Prints quality report. Returns stats."""
    print(f"Loading GitHub metadata from: {github_path}")
    github_items = load_github_metadata(github_path)
    print(f"  Loaded {len(github_items)} GitHub repos")

    print(f"Loading Clawhub skill metrics from: {skill_metrics_path}")
    clawhub_items = load_skill_metrics(skill_metrics_path)
    print(f"  Loaded {len(clawhub_items)} Clawhub skills")

    print("Building integrated dataset...")
    dataset = build_integrated_dataset(github_items, clawhub_items)
    print(f"  Total rows: {len(dataset)}")

    print("Checking data quality...")
    quality = check_data_quality(dataset)

    print("\n--- Data Quality Report ---")
    print(f"Total rows: {quality['total_rows']}")
    print(f"Class counts: {quality['class_counts']}")
    if quality["class_balance_ratio"] is not None:
        print(f"Clawhub/GitHub ratio: {quality['class_balance_ratio']:.4f}")

    print("\nMissing rates (non-zero only):")
    for col, rate in quality["missing_rates"].items():
        if rate > 0:
            print(f"  {col}: {rate:.2%}")

    print("\nSkillability core distribution by class:")
    for label_val, stats in quality["skillability_by_class"].items():
        label_name = "Clawhub" if label_val == 1 else "GitHub"
        if stats.get("count", 0) > 0:
            print(
                f"  {label_name}: mean={stats.get('mean', 'N/A')}, "
                f"median={stats.get('median', 'N/A')}, "
                f"min={stats.get('min', 'N/A')}, max={stats.get('max', 'N/A')}"
            )
    print("---------------------------\n")

    print(f"Saving dataset to: {output_path}")
    save_dataset(dataset, output_path)
    print("Done.")

    return {
        "n_github": len(github_items),
        "n_clawhub": len(clawhub_items),
        "total_rows": len(dataset),
        "quality_report": quality,
        "output_path": output_path,
    }


if __name__ == "__main__":
    import sys
    from pathlib import Path as _Path

    # Resolve paths relative to project root (this file is at validation/integrate_data.py)
    _project_root = _Path(__file__).parent.parent
    _github_path = str(_project_root / "output" / "validation" / "github_metadata_extended.json")
    _skill_metrics_path = str(_project_root / "output" / "validation" / "skill_metrics.json")
    _output_path = str(_project_root / "output" / "validation" / "integrated_data.csv")

    # Allow overrides via CLI args
    if len(sys.argv) >= 4:
        _github_path = sys.argv[1]
        _skill_metrics_path = sys.argv[2]
        _output_path = sys.argv[3]

    stats = integrate_data(_github_path, _skill_metrics_path, _output_path)
    print(f"Integration complete. {stats['total_rows']} rows written to {stats['output_path']}")
