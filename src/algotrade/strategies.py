"""Signal generators. Each strategy function takes a close price series and
returns a (entries, exits) pair of boolean Series suitable for
``vectorbt.Portfolio.from_signals``.
"""

from __future__ import annotations

from typing import Callable

import pandas as pd
import vectorbt as vbt

Signals = tuple[pd.Series, pd.Series]


def ma_crossover_signals(close: pd.Series, fast: int = 20, slow: int = 50) -> Signals:
    """Trend-following: long while the fast SMA is above the slow SMA."""
    fast_ma = vbt.MA.run(close, window=fast)
    slow_ma = vbt.MA.run(close, window=slow)
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)
    return entries, exits


def rsi_mean_reversion_signals(
    close: pd.Series, window: int = 14, lower: int = 30, upper: int = 70
) -> Signals:
    """Contrarian: buy when RSI exits oversold, sell when it enters overbought."""
    rsi = vbt.RSI.run(close, window=window)
    entries = rsi.rsi_crossed_above(lower)
    exits = rsi.rsi_crossed_above(upper)
    return entries, exits


def golden_cross_signals(close: pd.Series, fast: int = 20, long: int = 200) -> Signals:
    """Long-term trend filter: the classic golden cross / death cross."""
    fast_ma = vbt.MA.run(close, window=fast)
    long_ma = vbt.MA.run(close, window=long)
    entries = fast_ma.ma_crossed_above(long_ma)
    exits = fast_ma.ma_crossed_below(long_ma)
    return entries, exits


# Registry used by the comparison/sweep/walk-forward scripts so new strategies
# only need to be added in one place.
STRATEGIES: dict[str, Callable[..., Signals]] = {
    "ma_crossover": ma_crossover_signals,
    "rsi_mean_reversion": rsi_mean_reversion_signals,
    "golden_cross": golden_cross_signals,
}

DEFAULT_PARAMS: dict[str, dict] = {
    "ma_crossover": {"fast": 20, "slow": 50},
    "rsi_mean_reversion": {"window": 14, "lower": 30, "upper": 70},
    "golden_cross": {"fast": 20, "long": 200},
}
