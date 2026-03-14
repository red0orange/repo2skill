"""Main preprocessing pipeline: load CSV, engineer features, create train/test split."""

import csv
import json
import math
import random
from pathlib import Path
from validation.features import (
    extract_features_for_classification,
    extract_features_for_performance,
    get_top_languages,
    log_transform,
)
from validation.config_validation import (
    PROCESSED_DATA_PATH, VALIDATION_OUTPUT_DIR, RANDOM_STATE
)


def load_integrated_data(path: str) -> list:
    """Load CSV into list of row dicts. Cast types (int, float, bool)."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Cast numeric fields
            for int_field in [
                "label", "task_clarity", "interface_clarity", "composability",
                "automation_value", "deployment_friction", "operational_risk",
                "github_stars"
            ]:
                if row.get(int_field) not in (None, ""):
                    try:
                        row[int_field] = int(row[int_field])
                    except (ValueError, TypeError):
                        row[int_field] = 0
                else:
                    row[int_field] = 0

            for float_field in ["skillability_core", "opportunity_score"]:
                if row.get(float_field) not in (None, ""):
                    try:
                        row[float_field] = float(row[float_field])
                    except (ValueError, TypeError):
                        row[float_field] = 0.0
                else:
                    row[float_field] = 0.0

            # Clawhub-specific int fields (may be empty for GitHub items)
            for clawhub_int_field in [
                "clawhub_stars", "clawhub_downloads", "clawhub_installs", "clawhub_versions"
            ]:
                if row.get(clawhub_int_field) not in (None, ""):
                    try:
                        row[clawhub_int_field] = int(row[clawhub_int_field])
                    except (ValueError, TypeError):
                        row[clawhub_int_field] = 0
                else:
                    row[clawhub_int_field] = None  # Keep None for GitHub items

            rows.append(row)
    return rows


def create_classification_dataset(rows: list) -> tuple:
    """
    Create (X, y) for binary classification.
    X: list of feature dicts
    y: list of int labels (0 or 1)

    Note: dataset is imbalanced (12.6:1). Apply class_weight='balanced' at model time.
    """
    top_languages = get_top_languages(rows, n=15)
    X = []
    y = []
    for row in rows:
        features = extract_features_for_classification(row, top_languages)
        X.append(features)
        y.append(int(row["label"]))
    return X, y


def create_performance_dataset(rows: list) -> tuple:
    """
    Create (X, y) for Clawhub marketplace performance.
    Only uses Clawhub items (label==1).
    X: list of feature dicts
    y: list of float (log(clawhub_downloads + 1))
    """
    X = []
    y = []
    for row in rows:
        features = extract_features_for_performance(row)
        if features is None:
            continue
        # Use log(clawhub_downloads + 1) as the performance target
        downloads = row.get("clawhub_downloads")
        if downloads is None:
            downloads = 0
        log_downloads = log_transform(downloads, add=1)
        X.append(features)
        y.append(log_downloads)
    return X, y


def train_test_split_stratified(X: list, y: list, test_size: float = 0.2, random_state: int = 42) -> tuple:
    """Stratified split: preserve class balance in both train and test."""
    rng = random.Random(random_state)

    # Group indices by class
    class_indices = {}
    for i, label in enumerate(y):
        class_indices.setdefault(label, []).append(i)

    train_indices = []
    test_indices = []

    for label, indices in class_indices.items():
        shuffled = indices[:]
        rng.shuffle(shuffled)
        n_test = max(1, int(len(shuffled) * test_size))
        test_indices.extend(shuffled[:n_test])
        train_indices.extend(shuffled[n_test:])

    # Shuffle the final sets
    rng.shuffle(train_indices)
    rng.shuffle(test_indices)

    X_train = [X[i] for i in train_indices]
    X_test = [X[i] for i in test_indices]
    y_train = [y[i] for i in train_indices]
    y_test = [y[i] for i in test_indices]

    return X_train, X_test, y_train, y_test


def save_processed_data(
    X_train_cls, y_train_cls, X_test_cls, y_test_cls,
    X_train_perf, y_train_perf, X_test_perf, y_test_perf,
    feature_names_cls: list, feature_names_perf: list,
    output_dir: str
):
    """Save all splits as JSON files for use by modeling tasks."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    def save_json(obj, filename):
        with open(out / filename, "w", encoding="utf-8") as f:
            json.dump(obj, f)
        print(f"  Saved {filename} ({len(obj)} items)")

    print("Saving classification datasets...")
    save_json(X_train_cls, "X_train_classification.json")
    save_json(y_train_cls, "y_train_classification.json")
    save_json(X_test_cls, "X_test_classification.json")
    save_json(y_test_cls, "y_test_classification.json")
    save_json(feature_names_cls, "feature_names_classification.json")

    print("Saving performance datasets...")
    save_json(X_train_perf, "X_train_performance.json")
    save_json(y_train_perf, "y_train_performance.json")
    save_json(X_test_perf, "X_test_performance.json")
    save_json(y_test_perf, "y_test_performance.json")
    save_json(feature_names_perf, "feature_names_performance.json")


def preprocess(integrated_path: str, output_dir: str):
    """Main pipeline. Prints dataset statistics."""
    print(f"Loading data from: {integrated_path}")
    rows = load_integrated_data(integrated_path)
    print(f"  Total rows: {len(rows)}")

    clawhub_rows = [r for r in rows if r["label"] == 1]
    github_rows = [r for r in rows if r["label"] == 0]
    print(f"  Clawhub (label=1): {len(clawhub_rows)}")
    print(f"  GitHub  (label=0): {len(github_rows)}")
    ratio = len(github_rows) / len(clawhub_rows) if clawhub_rows else 0
    print(f"  Class imbalance ratio: {ratio:.1f}:1 (GitHub:Clawhub)")

    print("\nEngineering classification features...")
    X_cls, y_cls = create_classification_dataset(rows)
    feature_names_cls = list(X_cls[0].keys()) if X_cls else []
    print(f"  Classification features: {len(feature_names_cls)}")
    print(f"  Classification samples: {len(X_cls)}")

    print("\nEngineering performance features...")
    X_perf, y_perf = create_performance_dataset(rows)
    feature_names_perf = list(X_perf[0].keys()) if X_perf else []
    print(f"  Performance features: {len(feature_names_perf)}")
    print(f"  Performance samples (Clawhub only): {len(X_perf)}")

    print("\nCreating stratified train/test splits...")
    X_train_cls, X_test_cls, y_train_cls, y_test_cls = train_test_split_stratified(
        X_cls, y_cls, test_size=0.2, random_state=RANDOM_STATE
    )
    print(f"  Classification train: {len(X_train_cls)} ({sum(y_train_cls)} positive)")
    print(f"  Classification test:  {len(X_test_cls)} ({sum(y_test_cls)} positive)")

    X_train_perf, X_test_perf, y_train_perf, y_test_perf = train_test_split_stratified(
        X_perf, [0] * len(X_perf), test_size=0.2, random_state=RANDOM_STATE
    )
    # For performance, y is continuous — re-align after index splitting
    # We need to preserve order, so redo with direct index split
    perf_indices = list(range(len(X_perf)))
    rng = random.Random(RANDOM_STATE)
    rng.shuffle(perf_indices)
    n_test_perf = max(1, int(len(perf_indices) * 0.2))
    test_idx_perf = set(perf_indices[:n_test_perf])
    train_idx_perf = [i for i in range(len(X_perf)) if i not in test_idx_perf]
    test_idx_perf_list = [i for i in perf_indices[:n_test_perf]]

    X_train_perf = [X_perf[i] for i in train_idx_perf]
    y_train_perf = [y_perf[i] for i in train_idx_perf]
    X_test_perf = [X_perf[i] for i in test_idx_perf_list]
    y_test_perf = [y_perf[i] for i in test_idx_perf_list]

    print(f"  Performance train: {len(X_train_perf)}")
    print(f"  Performance test:  {len(X_test_perf)}")

    print("\nFeature names (classification):")
    for fn in feature_names_cls:
        print(f"  {fn}")

    print("\nSaving processed data...")
    save_processed_data(
        X_train_cls, y_train_cls, X_test_cls, y_test_cls,
        X_train_perf, y_train_perf, X_test_perf, y_test_perf,
        feature_names_cls, feature_names_perf,
        output_dir
    )
    print("\nPreprocessing complete.")


if __name__ == "__main__":
    import os
    # Resolve paths relative to this file
    _here = Path(__file__).parent.parent
    integrated_path = str(_here / "output" / "validation" / "integrated_data.csv")
    output_dir = str(_here / "output" / "validation")
    preprocess(integrated_path, output_dir)
