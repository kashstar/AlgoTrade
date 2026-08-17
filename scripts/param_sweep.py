#!/usr/bin/env python
"""Grid search MA Crossover / Golden Cross windows and report the best combos.

This is a full-sample, in-sample sweep - useful for finding a robust
parameter neighborhood, but it will happily overfit if you pick the single
best cell and trust it blindly. See `scripts/walk_forward.py` for an
out-of-sample check on whatever you find here.

Usage:
    python scripts/param_sweep.py
    python scripts/param_sweep.py --data data/tutorial.csv --top 15
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from algotrade.backtest import run_backtest
from algotrade.data import load_ohlc
from algotrade.strategies import golden_cross_signals

FAST_WINDOWS = [5, 10, 15, 20, 25, 30, 40, 50]
SLOW_WINDOWS = [20, 30, 50, 75, 100, 150, 180, 200, 220]


def sweep(close: pd.Series, fees: float, freq: str) -> pd.DataFrame:
    rows = []
    for fast in FAST_WINDOWS:
        for slow in SLOW_WINDOWS:
            if fast >= slow:
                continue
            entries, exits = golden_cross_signals(close, fast=fast, long=slow)
            pf = run_backtest(close, entries, exits, fees=fees, freq=freq)
            rows.append(
                {
                    "fast": fast,
                    "slow": slow,
                    "total_return_pct": pf.total_return() * 100,
                    "sharpe_ratio": pf.sharpe_ratio(),
                    "max_drawdown_pct": pf.max_drawdown() * 100,
                    "trades": pf.trades.count(),
                }
            )
    return pd.DataFrame(rows).sort_values("total_return_pct", ascending=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/tutorial.csv")
    parser.add_argument("--fees", type=float, default=0.001)
    parser.add_argument("--freq", default="1D")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--out", default="results/param_sweep.csv")
    args = parser.parse_args()

    df = load_ohlc(args.data)
    results = sweep(df["close"], fees=args.fees, freq=args.freq)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.out, index=False)

    hold_return = (df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100
    print(f"Buy & hold return: {hold_return:.2f}%")
    print(f"Swept {len(results)} (fast, slow) SMA combinations")
    print(f"Full results saved to {args.out}\n")
    print(f"Top {args.top} by total return:")
    print(results.head(args.top).to_string(index=False))


if __name__ == "__main__":
    main()
