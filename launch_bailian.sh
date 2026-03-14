#!/bin/bash
# Launch large-scale analysis with Alibaba Bailian API

echo "=========================================="
echo "Large-Scale Software2Skill Analysis"
echo "Using Alibaba Bailian API"
echo "Target: 29,900 samples (10%)"
echo "Concurrency: 200"
echo "=========================================="
echo ""

cd /home/red0orange/Projects/OpenClawAnalysis/software2skill_analysis

# Check dependencies
echo "Checking dependencies..."
python -c "import aiohttp, tqdm" 2>/dev/null || {
    echo "Installing dependencies..."
    pip install aiohttp tqdm -q
}

echo "✓ Dependencies ready"
echo ""

# Create output directories
mkdir -p output_large/checkpoints output_large/figures

# Launch analysis in background
echo "Starting analysis with Bailian API..."
nohup python main_bailian.py > output_large/run_bailian.log 2>&1 &
PID=$!

echo "✓ Analysis started (PID: $PID)"
echo ""
echo "Monitor progress:"
echo "  python monitor_large.py"
echo ""
echo "Check logs:"
echo "  tail -f output_large/run_bailian.log"
echo ""
echo "Check status:"
echo "  python status.py"
echo ""
