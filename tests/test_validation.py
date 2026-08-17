import numpy as np
import pandas as pd

from algotrade.strategies import golden_cross_signals
from algotrade.validation import walk_forward_evaluate


def _trending_close(n: int = 1000) -> pd.Series:
    idx = pd.date_range("2018-01-01", periods=n, freq="D")
    rng = np.random.default_rng(42)
    drift = np.linspace(0, 0.3, n)
    noise = np.cumsum(rng.normal(0, 0.01, n))
    close = 100 * np.exp(drift + noise)
    return pd.Series(close, index=idx)


def test_walk_forward_evaluate_produces_one_fold_per_split():
    close = _trending_close()
    param_grid = [{"fast": f, "long": l} for f in (10, 20) for l in (100, 150)]
    result = walk_forward_evaluate(close, golden_cross_signals, param_grid, n_splits=3)
    assert len(result.folds) == 3


def test_walk_forward_folds_are_chronological_and_non_overlapping():
    close = _trending_close()
    param_grid = [{"fast": 20, "long": 100}]
    result = walk_forward_evaluate(close, golden_cross_signals, param_grid, n_splits=4)
    for prev, cur in zip(result.folds, result.folds[1:]):
        assert prev.test_end < cur.test_start
        assert cur.train_end >= prev.test_end


def test_walk_forward_result_aggregates():
    close = _trending_close()
    param_grid = [{"fast": 20, "long": 100}]
    result = walk_forward_evaluate(close, golden_cross_signals, param_grid, n_splits=3)
    assert isinstance(result.compounded_strategy_return, float)
    assert isinstance(result.compounded_benchmark_return, float)
    assert 0.0 <= result.win_rate <= 1.0
    frame = result.to_frame()
    assert len(frame) == 3
    assert "beat_benchmark" in frame.columns
