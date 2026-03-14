"""Configuration for software2skill analysis."""

from pathlib import Path

from config_shared import (
    CAPABILITY_CLASSES,
    DEFAULT_DATA_DIR,
    DEFAULT_BAILIAN_API_URL,
    DEFAULT_BAILIAN_MODEL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TEMPERATURE,
    EXECUTION_MODES,
    GRANULARITY_TYPES,
    OPPORTUNITY_WEIGHTS,
    PROJECT_ROOT,
    SKILLABILITY_WEIGHTS,
    env,
    env_path,
)

# Bailian API configuration
BAILIAN_API_KEY = env("BAILIAN_API_KEY")
BAILIAN_API_URL = env("BAILIAN_API_URL", DEFAULT_BAILIAN_API_URL)
BAILIAN_MODEL = env("BAILIAN_MODEL", DEFAULT_BAILIAN_MODEL)
BAILIAN_TEMPERATURE = float(env("BAILIAN_TEMPERATURE", str(DEFAULT_TEMPERATURE)))
BAILIAN_MAX_RETRIES = int(env("BAILIAN_MAX_RETRIES", str(DEFAULT_MAX_RETRIES)))
MAX_CONCURRENT_REQUESTS = int(env("MAX_CONCURRENT_REQUESTS", "20"))
BATCH_SIZE = int(env("BATCH_SIZE", "50"))

# Data paths
CLAWHUB_DATA_PATH = env_path("CLAWHUB_DATA_PATH", DEFAULT_DATA_DIR / "clawhub_skills_complete.json")
GITHUB_DATA_PATH = env_path("GITHUB_DATA_PATH", DEFAULT_DATA_DIR / "github_repos.jsonl")
README_DIR = env_path("README_DIR", DEFAULT_DATA_DIR / "readmes")

# Sample sizes
CLAWHUB_SAMPLE_SIZE = 50
GITHUB_SAMPLE_SIZE = 100

# Output paths
OUTPUT_DIR = env_path("OUTPUT_DIR", PROJECT_ROOT / "output")
EXTRACTED_DATA_PATH = str(Path(OUTPUT_DIR) / "extracted_data.json")
TOP_CANDIDATES_PATH = str(Path(OUTPUT_DIR) / "top_candidates.json")
ANALYSIS_REPORT_PATH = str(Path(OUTPUT_DIR) / "analysis_report.html")
FIGURES_DIR = str(Path(OUTPUT_DIR) / "figures")
