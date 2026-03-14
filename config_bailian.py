"""Large-scale parallel analysis configuration with Alibaba Bailian API."""

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Alibaba Bailian API Configuration
BAILIAN_API_KEY = "sk-b40c3570edf64a3fbca9a9bc8863c014"
BAILIAN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
BAILIAN_MODEL = "qwen-plus"  # 或 qwen-turbo, qwen-max
BAILIAN_TEMPERATURE = 0.1
BAILIAN_MAX_RETRIES = 3

# Parallel processing configuration
MAX_CONCURRENT_REQUESTS = 200  # 阿里云支持更高并发
BATCH_SIZE = 1000
CHECKPOINT_INTERVAL = 500

# Data paths
CLAWHUB_DATA_PATH = str(PROJECT_ROOT / "clawhub_skills_complete.json")
GITHUB_DATA_PATH = str(PROJECT_ROOT / "data" / "github_repos.jsonl")
README_DIR = str(PROJECT_ROOT / "data" / "readmes")

# Sample sizes for first version paper (10% of total)
CLAWHUB_SAMPLE_SIZE = 2200
GITHUB_SAMPLE_SIZE = 27700

# Output paths
OUTPUT_DIR = "output_large"
EXTRACTED_DATA_PATH = f"{OUTPUT_DIR}/extracted_data.jsonl"
TOP_CANDIDATES_PATH = f"{OUTPUT_DIR}/top_candidates.json"
ANALYSIS_REPORT_PATH = f"{OUTPUT_DIR}/analysis_report.html"
FIGURES_DIR = f"{OUTPUT_DIR}/figures"
CHECKPOINT_DIR = f"{OUTPUT_DIR}/checkpoints"

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
