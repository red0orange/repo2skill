"""Configuration for software2skill analysis."""

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# GLM API Configuration
GLM_API_KEY = "4de6c5e8c87947a09e497f6919ef29ac.mwkQLkcG3mYTPbJT"
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
GLM_MODEL = "glm-4-flash"
GLM_TEMPERATURE = 0.1
GLM_MAX_RETRIES = 3

# Data paths
CLAWHUB_DATA_PATH = str(PROJECT_ROOT / "clawhub_skills_complete.json")
GITHUB_DATA_PATH = str(PROJECT_ROOT / "data" / "github_repos.jsonl")
README_DIR = str(PROJECT_ROOT / "data" / "readmes")

# Sample sizes
CLAWHUB_SAMPLE_SIZE = 50
GITHUB_SAMPLE_SIZE = 100

# Output paths
OUTPUT_DIR = "output"
EXTRACTED_DATA_PATH = f"{OUTPUT_DIR}/extracted_data.json"
TOP_CANDIDATES_PATH = f"{OUTPUT_DIR}/top_candidates.json"
ANALYSIS_REPORT_PATH = f"{OUTPUT_DIR}/analysis_report.html"
FIGURES_DIR = f"{OUTPUT_DIR}/figures"

# Taxonomy
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
