"""Large-scale parallel analysis configuration."""

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# GLM API Configuration
GLM_API_KEY = "4de6c5e8c87947a09e497f6919ef29ac.mwkQLkcG3mYTPbJT"
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
GLM_MODEL = "glm-4-flash"
GLM_TEMPERATURE = 0.1
GLM_MAX_RETRIES = 3

# Parallel processing configuration
MAX_CONCURRENT_REQUESTS = 100  # 并发数，可根据API限制调整
BATCH_SIZE = 1000  # 每批处理的数量
CHECKPOINT_INTERVAL = 500  # 每处理多少个保存一次checkpoint

# Data paths
CLAWHUB_DATA_PATH = str(PROJECT_ROOT / "clawhub_skills_complete.json")
GITHUB_DATA_PATH = str(PROJECT_ROOT / "data" / "github_repos.jsonl")
README_DIR = str(PROJECT_ROOT / "data" / "readmes")

# Sample sizes for first version paper (10% of total)
CLAWHUB_SAMPLE_SIZE = 2200  # ~10% of 22,413
GITHUB_SAMPLE_SIZE = 27700  # ~10% of 276,961

# Output paths
OUTPUT_DIR = "output_large"
EXTRACTED_DATA_PATH = f"{OUTPUT_DIR}/extracted_data.jsonl"  # Use JSONL for large data
TOP_CANDIDATES_PATH = f"{OUTPUT_DIR}/top_candidates.json"
ANALYSIS_REPORT_PATH = f"{OUTPUT_DIR}/analysis_report.html"
FIGURES_DIR = f"{OUTPUT_DIR}/figures"
CHECKPOINT_DIR = f"{OUTPUT_DIR}/checkpoints"

# Taxonomy (same as before)
CAPABILITY_CLASSES = [
    "code_devops",
    "data_retrieval_search",
    "document_processing",
    "web_automation",
    "communication_collaboration",
    "knowledge_workflow_research",
    "business_productivity_ops",
    "multimedia_content",
    "system_infrastructure",
    "external_service_connector"
]

GRANULARITY_TYPES = [
    "primitive_tool",
    "service_wrapper",
    "workflow_skill",
    "platform_adapter"
]

EXECUTION_MODES = [
    "local_deterministic",
    "remote_api_mediated",
    "browser_mediated",
    "human_in_the_loop",
    "hybrid"
]

# Scoring weights
SKILLABILITY_WEIGHTS = {
    "task_clarity": 0.25,
    "interface_clarity": 0.20,
    "composability": 0.20,
    "automation_value": 0.25,
    "deployment_friction": -0.05,
    "operational_risk": -0.05
}

OPPORTUNITY_WEIGHTS = {
    "skillability_core": 0.6,
    "repo_quality": 0.4
}
