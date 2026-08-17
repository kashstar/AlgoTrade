"""Walk-forward validation.

A single full-history backtest can't tell you whether a strategy's edge is
real or just curve-fit to that one history. Walk-forward validation selects
parameters on a training window using only data available at that point,
then measures performance on the following, unseen test window - repeated
across several rolling folds - which is a much more honest estimate of
out-of-sample performance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

from algotrade.backtest import run_backtest
from algotrade.strategies import Signals


@dataclass
class Fold:
    split: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    best_params: dict
    train_score: float
    strategy_return: float
    benchmark_return: float

    @property
    def beat_benchmark(self) -> bool:
        return self.strategy_return > self.benchmark_return


@dataclass
class WalkForwardResult:
    folds: list[Fold] = field(default_factory=list)

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame([vars(f) | {"beat_benchmark": f.beat_benchmark} for f in self.folds])

    @property
    def compounded_strategy_return(self) -> float:
        r = 1.0
        for f in self.folds:
            r *= 1 + f.strategy_return
        return r - 1

    @property
    def compounded_benchmark_return(self) -> float:
        r = 1.0
        for f in self.folds:
            r *= 1 + f.benchmark_return
        return r - 1

    @property
    def win_rate(self) -> float:
        if not self.folds:
            return float("nan")
        return sum(f.beat_benchmark for f in self.folds) / len(self.folds)


def _generate_splits(n_rows: int, n_splits: int, test_size: int) -> list[tuple[int, int, int, int]]:
    """Expanding-window splits: train always starts at 0 and grows; each test
    fold is a fresh, contiguous, never-before-seen block of `test_size` rows.
    """
    splits = []
    train_end = n_rows - n_splits * test_size
    if train_end <= 0:
        raise ValueError(
            f"Not enough data for {n_splits} folds of size {test_size} "
            f"({n_rows} rows available)."
        )
    for _ in range(n_splits):
        test_start = train_end
        test_end = min(test_start + test_size, n_rows)
        splits.append((0, train_end, test_start, test_end))
        train_end = test_end
    return splits


def walk_forward_evaluate(
    close: pd.Series,
    strategy_fn: Callable[..., Signals],
    param_grid: list[dict],
    *,
    n_splits: int = 5,
    test_size: int | None = None,
    select_metric: str = "total_return",
    init_cash: float = 10_000,
    fees: float = 0.001,
    freq: str = "1D",
) -> WalkForwardResult:
    """Run expanding-window walk-forward validation for one strategy.

    For each fold: pick the best params by backtesting each candidate in
    `param_grid` on the training window only, then apply that winning
    param set forward and measure its return over the held-out test window.
    """
    n = len(close)
    test_size = test_size or n // (n_splits + 2)
    splits = _generate_splits(n, n_splits, test_size)

    result = WalkForwardResult()
    for i, (tr_s, tr_e, te_s, te_e) in enumerate(splits):
        train_close = close.iloc[tr_s:tr_e]

        best_params, best_score = None, float("-inf")
        for params in param_grid:
            entries, exits = strategy_fn(train_close, **params)
            pf = run_backtest(train_close, entries, exits, init_cash=init_cash, fees=fees, freq=freq)
            score = pf.stats(metrics=[select_metric]).iloc[0]
            if pd.notna(score) and score > best_score:
                best_params, best_score = params, score

        # Re-run the winning params on history up to (and including) the test
        # window, so indicators have proper warmup and any position open at
        # the train/test boundary carries over realistically.
        full_close = close.iloc[tr_s:te_e]
        entries, exits = strategy_fn(full_close, **best_params)
        pf = run_backtest(full_close, entries, exits, init_cash=init_cash, fees=fees, freq=freq)
        value = pf.value()

        baseline_idx = te_s - tr_s - 1
        strategy_return = value.iloc[-1] / value.iloc[baseline_idx] - 1
        benchmark_return = full_close.iloc[-1] / full_close.iloc[baseline_idx] - 1

        result.folds.append(
            Fold(
                split=i,
                train_start=close.index[tr_s],
                train_end=close.index[tr_e - 1],
                test_start=close.index[te_s],
                test_end=close.index[te_e - 1],
                best_params=best_params,
                train_score=best_score,
                strategy_return=strategy_return,
                benchmark_return=benchmark_return,
            )
        )

    return result
