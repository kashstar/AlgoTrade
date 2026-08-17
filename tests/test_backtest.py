import numpy as np
import pandas as pd

from algotrade.backtest import compare_strategies, run_backtest
from algotrade.strategies import DEFAULT_PARAMS, STRATEGIES


def _trending_close(n: int = 400) -> pd.Series:
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    up = np.linspace(100, 300, n // 2)
    down = np.linspace(300, 150, n - n // 2)
    return pd.Series(np.concatenate([up, down]), index=idx)


def test_run_backtest_starts_at_init_cash():
    close = _trending_close()
    entries = pd.Series(False, index=close.index)
    exits = pd.Series(False, index=close.index)
    entries.iloc[10] = True  # buy once, never sell
    pf = run_backtest(close, entries, exits, init_cash=10_000, fees=0.0, freq="1D")
    assert pf.init_cash == 10_000


def test_compare_strategies_returns_one_row_per_strategy_plus_benchmark():
    close = _trending_close()
    signals = {name: fn(close, **DEFAULT_PARAMS[name]) for name, fn in STRATEGIES.items()}
    result = compare_strategies(close, signals)
    assert "Buy & Hold" in result.index
    for name in STRATEGIES:
        assert name in result.index
    assert "Total Return [%]" in result.columns
