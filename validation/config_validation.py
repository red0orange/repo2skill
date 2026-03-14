"""Configuration for validation experiments."""

# Output paths
VALIDATION_OUTPUT_DIR = "output/validation"
MATCHES_PATH = f"{VALIDATION_OUTPUT_DIR}/clawhub_github_matches.json"
SKILL_METRICS_PATH = f"{VALIDATION_OUTPUT_DIR}/skill_metrics.json"
GITHUB_METADATA_PATH = f"{VALIDATION_OUTPUT_DIR}/github_metadata_extended.json"
PROCESSED_DATA_PATH = f"{VALIDATION_OUTPUT_DIR}/processed_data.csv"

# Model paths
MODELS_DIR = f"{VALIDATION_OUTPUT_DIR}/models"
BASELINE_MODEL_PREFIX = f"{MODELS_DIR}/baseline"
FULL_MODEL_PREFIX = f"{MODELS_DIR}/full"

# Analysis paths
ANALYSIS_DIR = f"{VALIDATION_OUTPUT_DIR}/analysis"
FIGURES_DIR = f"{VALIDATION_OUTPUT_DIR}/figures"

# GitHub API
GITHUB_API_TOKEN = None  # Set via environment variable GITHUB_TOKEN
GITHUB_API_BASE = "https://api.github.com"
GITHUB_RATE_LIMIT = 5000  # requests per hour with auth

# Model hyperparameters
RANDOM_STATE = 42
CV_FOLDS = 5
N_BOOTSTRAP = 1000

# Data paths (computed relative to this file's location)
import subprocess
from pathlib import Path


def _get_repo_root() -> Path:
    """Get git repository root, works in worktrees too."""
    try:
        # git rev-parse --show-toplevel returns the actual root (may be worktree root)
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        repo_root = Path(root)

        # If we're in a worktree, the root might have .git/worktrees/
        # Navigate up to find the common root with data/clawhub/
        if (repo_root.parent / "data" / "clawhub" / "clawhub_skills_complete.json").exists():
            return repo_root.parent
        if (repo_root / "data" / "clawhub" / "clawhub_skills_complete.json").exists():
            return repo_root

        # Otherwise, look up the directory tree for the main repo root
        current = Path(root)
        while current != current.parent:
            if (current / "data" / "clawhub" / "clawhub_skills_complete.json").exists():
                return current
            current = current.parent

        # If still not found, return what git told us
        return repo_root
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to path traversal - walk up to find data/clawhub/
        current = Path(__file__).parent
        while current != current.parent:
            if (current / "data" / "clawhub" / "clawhub_skills_complete.json").exists():
                return current
            current = current.parent

        # Last resort fallback (shouldn't reach here in normal operation)
        return Path(__file__).parent.parent.parent.parent


_REPO_ROOT = _get_repo_root()
_PROJECT_DIR = _REPO_ROOT / "software2skill_analysis"

CLAWHUB_COMPLETE_PATH = str(_REPO_ROOT / "data" / "clawhub" / "clawhub_skills_complete.json")
EXTRACTED_DATA_PATH = str(_PROJECT_DIR / "output_large" / "extracted_data.jsonl")
