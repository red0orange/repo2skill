"""Shared model training utilities."""
import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score
from sklearn.model_selection import StratifiedKFold
from validation.config_validation import CV_FOLDS, RANDOM_STATE

try:
    from xgboost import XGBClassifier
    _XGBOOST_AVAILABLE = True
except ImportError:
    _XGBOOST_AVAILABLE = False

BASELINE_FEATURE_PREFIXES = ["has_license", "archived"]

FULL_FEATURE_PREFIXES = [
    "has_license",
    "archived",
    "task_clarity",
    "interface_clarity",
    "composability",
    "automation_value",
    "deployment_friction",
    "operational_risk",
    "skillability_core",
    "cap_",
    "gran_",
]


def select_features(X: list, feature_names: list, prefixes: list) -> tuple:
    """
    Filter features to only those whose names start with any prefix.
    Returns (filtered_X, selected_feature_names).
    """
    selected_names = [
        name for name in feature_names
        if any(name.startswith(p) for p in prefixes)
    ]
    filtered_X = []
    for sample in X:
        filtered_sample = {k: v for k, v in sample.items() if k in selected_names}
        filtered_X.append(filtered_sample)
    return filtered_X, selected_names


def dicts_to_matrix(X: list, feature_names: list) -> np.ndarray:
    """Convert list of feature dicts to numpy array, in feature_names order."""
    n_samples = len(X)
    n_features = len(feature_names)
    matrix = np.zeros((n_samples, n_features), dtype=np.float64)
    for i, sample in enumerate(X):
        for j, name in enumerate(feature_names):
            matrix[i, j] = float(sample.get(name, 0.0))
    return matrix


def compute_metrics(y_true, y_pred_proba) -> dict:
    """
    Compute evaluation metrics.
    Returns: {auc_roc, pr_auc, precision_at_k}
    where k = number of positives in y_true
    """
    y_true = np.array(y_true)
    y_pred_proba = np.array(y_pred_proba)

    auc_roc = roc_auc_score(y_true, y_pred_proba)
    pr_auc = average_precision_score(y_true, y_pred_proba)

    # Precision at k: rank by predicted probability, take top-k, compute precision
    k = int(np.sum(y_true))
    if k == 0:
        precision_at_k = 0.0
    else:
        top_k_indices = np.argsort(y_pred_proba)[::-1][:k]
        precision_at_k = float(np.mean(y_true[top_k_indices]))

    return {
        "auc_roc": float(auc_roc),
        "pr_auc": float(pr_auc),
        "precision_at_k": float(precision_at_k),
    }


def train_logistic_regression(X_train, y_train) -> object:
    """Train LR with class_weight='balanced', C=1.0."""
    model = LogisticRegression(
        C=1.0,
        class_weight="balanced",
        max_iter=1000,
        random_state=RANDOM_STATE,
        solver="lbfgs",
    )
    model.fit(X_train, y_train)
    return model


def train_random_forest(X_train, y_train) -> object:
    """Train RF with n_estimators=100, class_weight='balanced'."""
    model = RandomForestClassifier(
        n_estimators=100,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def train_xgboost(X_train, y_train) -> object:
    """Train XGBoost with scale_pos_weight=neg_count/pos_count to handle imbalance."""
    if not _XGBOOST_AVAILABLE:
        raise ImportError("xgboost is not installed. Please install it with: pip install xgboost")

    y_arr = np.array(y_train)
    pos_count = int(np.sum(y_arr))
    neg_count = int(len(y_arr) - pos_count)
    scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0

    model = XGBClassifier(
        scale_pos_weight=scale_pos_weight,
        n_estimators=100,
        random_state=RANDOM_STATE,
        eval_metric="logloss",
        use_label_encoder=False,
        verbosity=0,
    )
    model.fit(X_train, y_train)
    return model


def cross_validate_model(model_fn, X, y, cv_folds=CV_FOLDS) -> dict:
    """
    5-fold stratified CV. Returns {mean_auc, std_auc, mean_pr_auc, std_pr_auc, fold_results}.
    """
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=RANDOM_STATE)
    X_arr = np.array(X) if not isinstance(X, np.ndarray) else X
    y_arr = np.array(y)

    fold_results = []
    aucs = []
    pr_aucs = []

    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(X_arr, y_arr)):
        X_fold_train = X_arr[train_idx]
        y_fold_train = y_arr[train_idx]
        X_fold_val = X_arr[val_idx]
        y_fold_val = y_arr[val_idx]

        model = model_fn(X_fold_train, y_fold_train)
        y_pred_proba = model.predict_proba(X_fold_val)[:, 1]
        metrics = compute_metrics(y_fold_val, y_pred_proba)

        fold_results.append({
            "fold": fold_idx + 1,
            "auc_roc": metrics["auc_roc"],
            "pr_auc": metrics["pr_auc"],
            "precision_at_k": metrics["precision_at_k"],
        })
        aucs.append(metrics["auc_roc"])
        pr_aucs.append(metrics["pr_auc"])

    return {
        "mean_auc": float(np.mean(aucs)),
        "std_auc": float(np.std(aucs)),
        "mean_pr_auc": float(np.mean(pr_aucs)),
        "std_pr_auc": float(np.std(pr_aucs)),
        "fold_results": fold_results,
    }


def save_model_results(results: dict, path: str):
    """Save results as JSON (convert numpy types to Python native)."""
    import pathlib
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)

    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert(v) for v in obj]
        return obj

    serializable = convert(results)
    with open(path, "w") as f:
        json.dump(serializable, f, indent=2)
