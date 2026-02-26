"""
Grid Trading Strategy for Freqtrade
===================================
A grid trading bot that places buy and sell orders at regular price intervals.

Risk Rules (Moderate):
- Max position size: 2% of portfolio per trade
- Max drawdown: 15% - stop trading if reached
- Stop loss: Hard stop at 15% drawdown
"""

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import pandas as pd
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class GridStrategy(IStrategy):
    """
    Grid Trading Strategy
    - Places orders at grid levels
    - Profits from price oscillations
    - Lower risk than directional trading
    """

    # Strategy parameters
    timeframe = "15m"
    minimal_roi = {
        "0": 0.01,  # 1% profit target
    }
    stoploss = -0.15  # 15% stop loss (matches drawdown limit)

    # Grid parameters
    grid_levels = 10  # Number of grid levels
    grid_spacing_pct = 0.005  # 0.5% between each grid level

    def __init__(self, config: dict):
        super().__init__(config)
        self.grid_levels = config.get("grid_levels", self.grid_levels)
        self.grid_spacing_pct = config.get("grid_spacing_pct", self.grid_spacing_pct)
        self.entry_grid = []
        self.exit_grid = []
        self.base_price = None
        self.total_trades = 0
        self.initial_balance = config.get("dry_run_wallet_balance", 1000)
        self.current_drawdown = 0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Populate indicators for the strategy"""
        # Calculate grid levels based on recent price
        if self.base_price is None and len(dataframe) > 0:
            self.base_price = dataframe["close"].iloc[-1]

        # Simple moving averages for trend detection
        dataframe["sma_20"] = dataframe["close"].rolling(window=20).mean()
        dataframe["sma_50"] = dataframe["close"].rolling(window=50).mean()

        # Price volatility
        dataframe["volatility"] = dataframe["close"].rolling(window=20).std()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Populate entry signals"""
        # Grid entry: buy when price drops to grid level
        if len(dataframe) > 0:
            current_price = dataframe["close"].iloc[-1]

            # Calculate grid entry points (buy levels)
            for i in range(1, self.grid_levels + 1):
                entry_price = self.base_price * (1 - (i * self.grid_spacing_pct))

                if current_price <= entry_price:
                    dataframe.loc[dataframe.index[-1], "enter_long"] = 1
                    break

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Populate exit signals"""
        # Grid exit: sell when price rises to upper grid level
        if len(dataframe) > 0:
            current_price = dataframe["close"].iloc[-1]

            # Calculate grid exit points (sell levels)
            for i in range(1, self.grid_levels + 1):
                exit_price = self.base_price * (1 + (i * self.grid_spacing_pct))

                if current_price >= exit_price:
                    dataframe.loc[dataframe.index[-1], "exit_long"] = 1
                    break

        return dataframe

    def check_entry(self, pair: str, dataframe: DataFrame) -> bool:
        """Custom entry check with risk management"""
        if self.current_drawdown >= 15:
            logger.warning(
                f"Max drawdown reached ({self.current_drawdown}%). Stopping entries."
            )
            return False

        # Check position size limit (2% max)
        if self.config.get("dry_run", True):
            position_value = self.wallets.get_free_balance(pair.replace("/", ""))
            portfolio_value = sum(w.free for w in self.wallets.values())

            if portfolio_value > 0:
                position_pct = (position_value / portfolio_value) * 100
                if position_pct >= 2:
                    logger.info(
                        f"Max position size reached ({position_pct}%). Skipping entry."
                    )
                    return False

        return True

    def check_exit(self, pair: str, dataframe: DataFrame, trade) -> bool:
        """Custom exit check with risk management"""
        # Update drawdown
        if self.config.get("dry_run", True):
            current_balance = self.wallets.get_total()
            drawdown = (
                (self.initial_balance - current_balance) / self.initial_balance
            ) * 100
            self.current_drawdown = max(drawdown, self.current_drawdown)

        return True

    def leverage(
        self,
        pair: str,
        current_price: float,
        proposed_leverage: float,
        max_leverage: float,
        entry_price: float,
        side: str,
        **kwargs,
    ) -> float:
        """No leverage - keep it at 1x"""
        return 1.0

    def confirm_trade_entry(
        self,
        pair: str,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        current_time,
        entry_price,
        **kwargs,
    ) -> bool:
        """Confirm trade entry with risk check"""
        # Final risk check before entry
        if self.current_drawdown >= 15:
            logger.warning("Rejecting entry due to max drawdown")
            return False

        return True

    def confirm_trade_exit(
        self,
        pair: str,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        exit_reason: str,
        current_time,
        **kwargs,
    ) -> bool:
        """Confirm trade exit"""
        return True

    def get_valid_pair_list(self, whitelist: list = None) -> list:
        """Get valid trading pairs"""
        if whitelist is None:
            whitelist = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
        return whitelist
