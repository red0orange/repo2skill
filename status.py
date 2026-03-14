#!/usr/bin/env python3
"""Quick status check for large-scale analysis."""

import json
from pathlib import Path
from datetime import datetime
import subprocess

def main():
    print("=" * 60)
    print("Large-Scale Analysis Status")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check if process is running
    try:
        result = subprocess.run(
            ["pgrep", "-f", "main_large.py"],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            print("✓ Process running (PID: {})".format(result.stdout.strip()))
        else:
            print("✗ Process not running")
    except:
        print("? Cannot check process status")

    # Check checkpoint
    checkpoint_file = Path("output_large/checkpoints/extraction_checkpoint.jsonl")
    if checkpoint_file.exists():
        with open(checkpoint_file) as f:
            count = sum(1 for line in f if line.strip())
        progress = count / 29900 * 100
        print(f"✓ Progress: {count:,}/29,900 ({progress:.1f}%)")
    else:
        print("⏳ Checkpoint not created yet (initializing...)")

    # Check output files
    output_dir = Path("output_large")
    if output_dir.exists():
        files = {
            "extracted_data.jsonl": "Extracted data",
            "top_candidates.json": "Top candidates",
            "analysis_report.html": "HTML report",
        }

        print("\nOutput files:")
        for filename, desc in files.items():
            filepath = output_dir / filename
            if filepath.exists():
                size = filepath.stat().st_size / 1024  # KB
                print(f"  ✓ {desc}: {size:.1f} KB")
            else:
                print(f"  ⏳ {desc}: Not created yet")

    print("\n" + "=" * 60)
    print("Commands:")
    print("  Monitor: python monitor_large.py")
    print("  Logs: tail -f output_large/run.log")
    print("  Status: python status.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
