#!/usr/bin/env python
"""Walk-forward (out-of-sample) validation for the Golden Cross strategy.

The full-history backtest in main.ipynb shows Golden Cross beating buy &
hold by a wide margin - but that number is in-sample: the parameters
(SMA 20/200) were chosen with full knowledge of the whole history. This
script asks a harder question: if you had re-selected parameters using only
data available *at the time*, on a rolling basis, would it still have won?

Usage:
    python scripts/walk_forward.py
    python scripts/walk_forward.py --splits 6 --metric sharpe_ratio
"""

from __future__ import annotations

import argparse
from pathlib import Path

from algotrade.data import load_ohlc
from algotrade.strategies import golden_cross_signals
from algotrade.validation import walk_forward_evaluate

FAST_WINDOWS = [10, 15, 20, 25, 30]
LONG_WINDOWS = [150, 180, 200, 220]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/tutorial.csv")
    parser.add_argument("--splits", type=int, default=5)
    parser.add_argument("--metric", default="total_return", help="metric used to pick params on the train window")
    parser.add_argument("--fees", type=float, default=0.001)
    parser.add_argument("--freq", default="1D")
    parser.add_argument("--out", default="results/walk_forward.csv")
    args = parser.parse_args()

    df = load_ohlc(args.data)
    close = df["close"]

    param_grid = [{"fast": f, "long": l} for f in FAST_WINDOWS for l in LONG_WINDOWS if f < l]

    result = walk_forward_evaluate(
        close,
        golden_cross_signals,
        param_grid,
        n_splits=args.splits,
        select_metric=args.metric,
        fees=args.fees,
        freq=args.freq,
    )

    frame = result.to_frame()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.out, index=False)

    print(f"Golden Cross walk-forward validation ({args.splits} expanding folds)")
    print(f"Params re-selected each fold from {len(param_grid)} candidates by best in-sample {args.metric}\n")
    print(frame.to_string(index=False))
    print()
    print(f"Compounded out-of-sample strategy return: {result.compounded_strategy_return * 100:.2f}%")
    print(f"Compounded out-of-sample buy & hold return: {result.compounded_benchmark_return * 100:.2f}%")
    print(f"Folds where strategy beat buy & hold: {result.win_rate * 100:.0f}%")
    print(f"\nFull results saved to {args.out}")


if __name__ == "__main__":
    main()
