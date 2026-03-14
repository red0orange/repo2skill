"""Feature engineering functions for validation modeling."""

import math
from collections import Counter
from typing import Optional

SKILLABILITY_DIMS = [
    "task_clarity", "interface_clarity", "composability",
    "automation_value", "deployment_friction", "operational_risk"
]

VALID_CAPABILITIES = [
    "code_devops", "data_retrieval_search", "document_processing",
    "web_automation", "communication_collaboration", "knowledge_workflow_research",
    "business_productivity_ops", "multimedia_content", "system_infrastructure",
    "external_service_connector"
]

VALID_GRANULARITIES = ["primitive_tool", "service_wrapper", "workflow_skill", "platform_adapter"]


def parse_bool(val) -> int:
    """Convert "True"/"False"/1/0/True/False to 0 or 1."""
    if isinstance(val, bool):
        return 1 if val else 0
    if isinstance(val, int):
        return 1 if val else 0
    if isinstance(val, str):
        if val.strip().lower() == "true":
            return 1
        return 0
    return 0


def log_transform(val, add=1) -> float:
    """Apply log(val + add), handle None/NaN as 0."""
    if val is None:
        return 0.0
    try:
        v = float(val)
        if math.isnan(v):
            return 0.0
        return math.log(v + add)
    except (TypeError, ValueError):
        return 0.0


def encode_language(language, top_languages: list) -> dict:
    """One-hot encode language against top_languages list. Unknown/None -> all zeros."""
    result = {}
    lang_val = language if language is not None else ""
    lang_val = lang_val.strip()
    for lang in top_languages:
        key = f"lang_{lang.replace(' ', '_').replace('+', 'plus').replace('#', 'sharp')}"
        result[key] = 1 if lang_val == lang else 0
    return result


def encode_capability(cap) -> dict:
    """One-hot encode primary_capability. Unknown -> all zeros."""
    result = {}
    cap_val = cap if cap is not None else ""
    cap_val = cap_val.strip()
    for c in VALID_CAPABILITIES:
        key = f"cap_{c}"
        result[key] = 1 if cap_val == c else 0
    return result


def encode_granularity(gran) -> dict:
    """One-hot encode granularity. Unknown -> all zeros."""
    result = {}
    gran_val = gran if gran is not None else ""
    gran_val = gran_val.strip()
    for g in VALID_GRANULARITIES:
        key = f"gran_{g}"
        result[key] = 1 if gran_val == g else 0
    return result


def extract_features_for_classification(row: dict, top_languages: list) -> dict:
    """
    Extract feature dict for binary classification (Clawhub vs GitHub).

    Features to use (NO github_stars - confounded):
    - 6 skillability dimensions (as-is, 1-5)
    - skillability_core (0-1)
    - has_license (0/1)
    - archived (0/1)
    - language one-hot encoding
    - primary_capability one-hot encoding
    - granularity one-hot encoding

    Returns dict of {feature_name: float}
    """
    features = {}

    # 6 skillability dimensions (numeric 1-5)
    for dim in SKILLABILITY_DIMS:
        try:
            features[dim] = float(row.get(dim, 0) or 0)
        except (TypeError, ValueError):
            features[dim] = 0.0

    # skillability_core (0-1 float)
    try:
        features["skillability_core"] = float(row.get("skillability_core", 0) or 0)
    except (TypeError, ValueError):
        features["skillability_core"] = 0.0

    # has_license binary
    features["has_license"] = float(parse_bool(row.get("has_license", 0)))

    # archived binary
    features["archived"] = float(parse_bool(row.get("archived", 0)))

    # language one-hot
    features.update(encode_language(row.get("language", ""), top_languages))

    # primary_capability one-hot
    features.update(encode_capability(row.get("primary_capability", "")))

    # granularity one-hot
    features.update(encode_granularity(row.get("granularity", "")))

    return features


def get_top_languages(rows: list, n: int = 15) -> list:
    """Get top N most common languages from dataset."""
    lang_counts = Counter()
    for row in rows:
        lang = row.get("language", "")
        if lang and lang.strip():
            lang_counts[lang.strip()] += 1
    return [lang for lang, _ in lang_counts.most_common(n)]


def extract_features_for_performance(row: dict):
    """
    Extract features for marketplace performance prediction.
    Only for Clawhub items (label==1). Returns None for GitHub items.

    Target: log_downloads (already computed in skill_metrics.json)
    Features: 6 skillability dimensions + skillability_core
    """
    try:
        label = int(row.get("label", 0))
    except (TypeError, ValueError):
        label = 0

    if label != 1:
        return None

    features = {}

    # 6 skillability dimensions (numeric 1-5)
    for dim in SKILLABILITY_DIMS:
        try:
            features[dim] = float(row.get(dim, 0) or 0)
        except (TypeError, ValueError):
            features[dim] = 0.0

    # skillability_core (0-1 float)
    try:
        features["skillability_core"] = float(row.get("skillability_core", 0) or 0)
    except (TypeError, ValueError):
        features["skillability_core"] = 0.0

    return features
