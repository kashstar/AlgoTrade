import numpy as np
import pandas as pd
import pytest

from algotrade.strategies import (
    DEFAULT_PARAMS,
    STRATEGIES,
    golden_cross_signals,
    ma_crossover_signals,
    rsi_mean_reversion_signals,
)


@pytest.fixture
def close() -> pd.Series:
    # Deterministic (seeded) synthetic series long enough to warm up a
    # 200-window SMA: an uptrend into a downtrend, with noise so the fast/slow
    # MAs actually cross rather than one staying strictly above the other.
    n = 400
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    rng = np.random.default_rng(0)
    up = np.linspace(100, 300, n // 2)
    down = np.linspace(300, 150, n - n // 2)
    trend = np.concatenate([up, down])
    noise = np.cumsum(rng.normal(0, 3, n))
    return pd.Series(trend + noise, index=idx)


def test_ma_crossover_signals_are_boolean_and_aligned(close):
    entries, exits = ma_crossover_signals(close, fast=5, slow=20)
    assert entries.dtype == bool
    assert exits.dtype == bool
    assert entries.index.equals(close.index)
    assert not (entries & exits).any()  # never both true on the same bar


def test_ma_crossover_fires_on_uptrend_then_downtrend(close):
    entries, exits = ma_crossover_signals(close, fast=5, slow=20)
    assert entries.any(), "expected at least one bullish crossover"
    assert exits.any(), "expected at least one bearish crossover"


def test_rsi_mean_reversion_signals_shape(close):
    entries, exits = rsi_mean_reversion_signals(close, window=14, lower=30, upper=70)
    assert len(entries) == len(close)
    assert entries.dtype == bool and exits.dtype == bool


def test_golden_cross_requires_long_warmup(close):
    entries, exits = golden_cross_signals(close, fast=20, long=200)
    # Nothing can fire before the long SMA has enough data
    assert not entries.iloc[:200].any()


@pytest.mark.parametrize("name", STRATEGIES.keys())
def test_registry_functions_accept_default_params(name, close):
    fn = STRATEGIES[name]
    entries, exits = fn(close, **DEFAULT_PARAMS[name])
    assert entries.index.equals(close.index)
    assert exits.index.equals(close.index)
