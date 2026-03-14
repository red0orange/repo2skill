"""Shared configuration helpers for analysis entrypoints."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"

DEFAULT_GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
DEFAULT_GLM_MODEL = "glm-4-flash"
DEFAULT_BAILIAN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
DEFAULT_BAILIAN_MODEL = "qwen-plus"
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_RETRIES = 3

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
    "external_service_connector",
]

GRANULARITY_TYPES = [
    "primitive_tool",
    "service_wrapper",
    "workflow_skill",
    "platform_adapter",
]

EXECUTION_MODES = [
    "local_deterministic",
    "remote_api_mediated",
    "browser_mediated",
    "human_in_the_loop",
    "hybrid",
]

# The paper formula uses reverse-coded negative dimensions with positive weights.
SKILLABILITY_WEIGHTS = {
    "task_clarity": 0.25,
    "interface_clarity": 0.20,
    "composability": 0.20,
    "automation_value": 0.25,
    "deployment_friction": 0.05,
    "operational_risk": 0.05,
}

OPPORTUNITY_WEIGHTS = {
    "skillability_core": 0.6,
    "repo_quality": 0.4,
}


def env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Return a trimmed environment variable or the provided default."""
    value = os.getenv(name)
    if value is None:
        return default
    stripped = value.strip()
    return stripped or default


def env_path(name: str, default: Path) -> str:
    """Resolve a path from env, falling back to a repository-relative default."""
    raw_value = env(name)
    if raw_value is None:
        return str(default)
    return str(Path(raw_value).expanduser())
