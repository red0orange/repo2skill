#!/usr/bin/env python3
"""Test run with 1000 samples to verify the system."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Override config for test
import config_large as config
config.CLAWHUB_SAMPLE_SIZE = 100
config.GITHUB_SAMPLE_SIZE = 900
config.MAX_CONCURRENT_REQUESTS = 50  # Lower concurrency for test

print("=" * 60)
print("TEST RUN: 1,000 samples")
print("=" * 60)
print(f"Clawhub: {config.CLAWHUB_SAMPLE_SIZE}")
print(f"GitHub: {config.GITHUB_SAMPLE_SIZE}")
print(f"Concurrency: {config.MAX_CONCURRENT_REQUESTS}")
print("=" * 60)

# Import and run main
from main_large import main
import asyncio

asyncio.run(main())
