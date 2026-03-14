#!/bin/bash
# Launch large-scale analysis with monitoring

echo "=========================================="
echo "Large-Scale Software2Skill Analysis"
echo "Target: 29,900 samples (10%)"
echo "Concurrency: 100"
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
echo "Starting analysis..."
nohup python main_large.py > output_large/run.log 2>&1 &
PID=$!

echo "✓ Analysis started (PID: $PID)"
echo ""
echo "Monitor progress:"
echo "  python monitor_large.py"
echo ""
echo "Check logs:"
echo "  tail -f output_large/run.log"
echo ""
echo "Check status:"
echo "  ps aux | grep main_large.py"
echo ""
