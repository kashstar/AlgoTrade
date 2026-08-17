"""Thin wrappers around vectorbt.Portfolio for running and comparing backtests."""

from __future__ import annotations

import pandas as pd
import vectorbt as vbt

DEFAULT_METRICS = ["total_return", "sharpe_ratio", "max_dd", "win_rate", "total_trades"]


def run_backtest(
    close: pd.Series,
    entries: pd.Series,
    exits: pd.Series,
    *,
    init_cash: float = 10_000,
    fees: float = 0.001,
    freq: str = "1D",
) -> vbt.Portfolio:
    """Run a long-only signal backtest and return the resulting Portfolio."""
    return vbt.Portfolio.from_signals(
        close, entries, exits, init_cash=init_cash, fees=fees, freq=freq
    )


def compare_strategies(
    close: pd.Series,
    signals: dict[str, tuple[pd.Series, pd.Series]],
    *,
    init_cash: float = 10_000,
    fees: float = 0.001,
    freq: str = "1D",
    metrics: list[str] | None = None,
) -> pd.DataFrame:
    """Backtest a buy & hold benchmark plus each named strategy's signals, and
    return a DataFrame of key metrics, one row per strategy.
    """
    metrics = metrics or DEFAULT_METRICS
    pf_hold = vbt.Portfolio.from_holding(close, init_cash=init_cash, freq=freq)

    rows = {"Buy & Hold": pf_hold.stats(metrics=metrics)}
    for name, (entries, exits) in signals.items():
        pf = run_backtest(close, entries, exits, init_cash=init_cash, fees=fees, freq=freq)
        rows[name] = pf.stats(metrics=metrics)

    return pd.DataFrame(rows).T
