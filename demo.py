#!/usr/bin/env python3
"""Quick demo with small sample size."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Override sample sizes for quick demo
import config
config.CLAWHUB_SAMPLE_SIZE = 10
config.GITHUB_SAMPLE_SIZE = 20

# Run main
from main import main
main()
