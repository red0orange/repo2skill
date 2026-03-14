#!/usr/bin/env python3
"""Quick test script to verify modules work correctly."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing Software2Skill Analysis modules...")
print("=" * 60)

# Test 1: Config
print("\n[Test 1] Loading config...")
try:
    import config
    print(f"✓ Config loaded")
    print(f"  - Clawhub sample size: {config.CLAWHUB_SAMPLE_SIZE}")
    print(f"  - GitHub sample size: {config.GITHUB_SAMPLE_SIZE}")
    print(f"  - GLM model: {config.GLM_MODEL}")
except Exception as e:
    print(f"✗ Config failed: {e}")
    sys.exit(1)

# Test 2: Data Sampler
print("\n[Test 2] Testing data sampler...")
try:
    from data_sampler import load_clawhub_skills, load_github_repos

    # Test with small sample
    clawhub_skills = load_clawhub_skills(config.CLAWHUB_DATA_PATH, 5)
    print(f"✓ Loaded {len(clawhub_skills)} Clawhub skills")

    github_repos = load_github_repos(config.GITHUB_DATA_PATH, config.README_DIR, 5)
    print(f"✓ Loaded {len(github_repos)} GitHub repos")
except Exception as e:
    print(f"✗ Data sampler failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: GLM Client
print("\n[Test 3] Testing GLM client...")
try:
    from glm_client import GLMClient
    client = GLMClient(
        config.GLM_API_KEY,
        config.GLM_API_URL,
        config.GLM_MODEL,
        config.GLM_TEMPERATURE,
        config.GLM_MAX_RETRIES
    )
    print(f"✓ GLM client initialized")

    # Test with a simple item
    if clawhub_skills:
        print(f"  Testing extraction on: {clawhub_skills[0].get('displayName', 'Unknown')}")
        result = client.extract_structured_data(clawhub_skills[0], 'clawhub')
        if result:
            print(f"✓ Extraction successful")
            print(f"  - Primary capability: {result.get('primary_capability', 'N/A')}")
            print(f"  - Skillability score: {result.get('skillability_score', 'N/A')}")
        else:
            print(f"⚠️  Extraction returned None (API might be slow or rate limited)")
except Exception as e:
    print(f"✗ GLM client failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Scorer
print("\n[Test 4] Testing scorer...")
try:
    from scorer import calculate_skillability_core, calculate_repo_quality

    test_data = {
        'task_clarity': 4,
        'interface_clarity': 4,
        'composability': 3,
        'automation_value': 5,
        'deployment_friction': 2,
        'operational_risk': 2,
        'source': 'github',
        'stars': 10000,
        'license': 'MIT',
        'archived': False
    }

    skillability = calculate_skillability_core(test_data, config.SKILLABILITY_WEIGHTS)
    quality = calculate_repo_quality(test_data)

    print(f"✓ Scorer working")
    print(f"  - Skillability core: {skillability:.3f}")
    print(f"  - Repo quality: {quality:.3f}")
except Exception as e:
    print(f"✗ Scorer failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Analyzer
print("\n[Test 5] Testing analyzer...")
try:
    from analyzer import analyze_capability_distribution, generate_summary_stats

    test_items = [
        {'source': 'clawhub', 'primary_capability': 'code_devops', 'skillability_score': 4},
        {'source': 'github', 'primary_capability': 'data_retrieval_search', 'skillability_score': 3},
    ]

    cap_dist = analyze_capability_distribution(test_items)
    stats = generate_summary_stats(test_items)

    print(f"✓ Analyzer working")
    print(f"  - Total items: {stats['total_items']}")
except Exception as e:
    print(f"✗ Analyzer failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Module tests complete!")
print("=" * 60)
