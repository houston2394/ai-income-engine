#!/bin/bash
# AI Income Engine - Grid Trading Bot Launcher

# This script starts the Grid trading bot in paper trading mode

set -e

echo "=========================================="
echo "AI Income Engine - Grid Trading Bot"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if freqtrade is installed
if ! python -c "import freqtrade" 2>/dev/null; then
    echo "Installing freqtrade..."
    pip install freqtrade
fi

# Check for config
if [ ! -f "config/config.json" ]; then
    echo "ERROR: config/config.json not found!"
    echo "Please copy config/example_config.json to config/config.json and add your API keys"
    exit 1
fi

echo ""
echo "Starting Grid Trading Bot in PAPER TRADING mode..."
echo "Risk Rules: 2% max position, 15% drawdown stop"
echo ""

# Run freqtrade
freqtrade trade \
    --config config/config.json \
    --strategy GridStrategy \
    --dry-run

echo ""
echo "Trading bot stopped."
