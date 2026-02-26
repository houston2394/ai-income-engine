# AI Income Engine - Trading Bot

## Setup

This directory contains the trading bot setup using Freqtrade.

### Prerequisites

- Python 3.9+
- Binance testnet account

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install freqtrade
pip install freqtrade

# Copy config
cp config/example_config.json config/config.json

# Edit config.json with your Binance testnet API keys
```

### Configuration

Edit `config/config.json`:
- Set `api_key` and `api_secret` from Binance testnet
- Ensure `dry_run` is `true` for paper trading

### Running

```bash
# Start freqtrade
freqtrade trade -c config/config.json -s GridStrategy

# Or use the wrapper
./run_grid.sh
```

### Strategy: Grid Trading

The Grid strategy places buy and sell orders at regular price intervals (grid levels).
- Profits from price oscillations
- Lower risk than directional trading
- Works best in sideways markets

### Risk Rules (Moderate)

- Max position size: 2% of portfolio per trade
- Max15% ( drawdown: stop trading if reached)
- Stop loss: Hard stop at 15% drawdown

### Files

- `config/config.json` - Main configuration
- `strategies/grid_strategy.py` - Grid trading strategy
- `strategies/__init__.py` - Strategy package
- `run_grid.sh` - Quick start script

### Paper Trading

Paper trading is ENABLED by default. To switch to real trading:
1. Set `dry_run` to `false` in config.json
2. Add real API keys
3. Start with small capital ($100-500)
