"""Data sampling module for software2skill analysis."""

import json
import random
from pathlib import Path
from typing import List, Dict, Any


def load_clawhub_skills(file_path: str, sample_size: int) -> List[Dict[str, Any]]:
    """Load and sample Clawhub skills.

    Args:
        file_path: Path to Clawhub skills JSON file
        sample_size: Number of skills to sample

    Returns:
        List of sampled skill dictionaries
    """
    print(f"Loading Clawhub skills from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        skills = json.load(f)

    print(f"Total Clawhub skills: {len(skills)}")

    # Filter out invalid entries
    valid_skills = []
    for skill in skills:
        # Skip if missing essential fields
        if not skill.get('slug') or not skill.get('displayName'):
            continue
        # Skip if it's just a listing/index page
        if skill.get('metadata') and skill['metadata'].get('type') == 'listing':
            continue
        valid_skills.append(skill)

    print(f"Valid Clawhub skills: {len(valid_skills)}")

    # Random sample
    sampled = random.sample(valid_skills, min(sample_size, len(valid_skills)))
    print(f"Sampled {len(sampled)} Clawhub skills")

    return sampled


def load_github_repos(file_path: str, readme_dir: str, sample_size: int) -> List[Dict[str, Any]]:
    """Load and sample GitHub repositories.

    Args:
        file_path: Path to GitHub repos JSONL file
        readme_dir: Directory containing README files
        sample_size: Number of repos to sample

    Returns:
        List of sampled repo dictionaries with README content
    """
    print(f"Loading GitHub repos from {file_path}...")

    repos = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                repos.append(json.loads(line))

    print(f"Total GitHub repos: {len(repos)}")

    # Filter out invalid entries
    valid_repos = []
    readme_path = Path(readme_dir)

    for repo in repos:
        # Skip archived repos
        if repo.get('archived', False):
            continue

        # Skip awesome-lists and tutorials (heuristic)
        topics = repo.get('topics', [])
        if any(t in ['awesome-list', 'awesome', 'tutorial', 'tutorials'] for t in topics):
            continue

        # Skip if no description
        if not repo.get('description'):
            continue

        # Check if README exists (try both _ and __ separators)
        repo_name_single = repo['full_name'].replace('/', '_')
        repo_name_double = repo['full_name'].replace('/', '__')

        readme_file = readme_path / f"{repo_name_double}.md"
        if not readme_file.exists():
            readme_file = readme_path / f"{repo_name_single}.md"

        if readme_file.exists():
            repo['readme_path'] = str(readme_file)
            valid_repos.append(repo)

    print(f"Valid GitHub repos with README: {len(valid_repos)}")

    # Random sample
    sampled = random.sample(valid_repos, min(sample_size, len(valid_repos)))

    # Load README content
    for repo in sampled:
        try:
            with open(repo['readme_path'], 'r', encoding='utf-8', errors='ignore') as f:
                repo['readme_content'] = f.read()[:10000]  # Limit to first 10k chars
        except Exception as e:
            print(f"Warning: Failed to load README for {repo['full_name']}: {e}")
            repo['readme_content'] = ""

    print(f"Sampled {len(sampled)} GitHub repos")

    return sampled


def prepare_samples(clawhub_path: str, github_path: str, readme_dir: str,
                   clawhub_size: int, github_size: int) -> Dict[str, List[Dict]]:
    """Prepare samples from both Clawhub and GitHub.

    Returns:
        Dictionary with 'clawhub' and 'github' keys containing sampled data
    """
    random.seed(42)  # For reproducibility

    clawhub_samples = load_clawhub_skills(clawhub_path, clawhub_size)
    github_samples = load_github_repos(github_path, readme_dir, github_size)

    return {
        'clawhub': clawhub_samples,
        'github': github_samples
    }
