#!/usr/bin/env python
"""Generate the static PNG charts embedded in README.md.

GitHub's README renderer doesn't run interactive Plotly/JS, so the charts
used there are plain matplotlib PNGs generated from the same package used
everywhere else in this project. Regenerate after any change to the data,
strategies, or their parameters:

    python scripts/generate_charts.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from algotrade.backtest import run_backtest
from algotrade.data import load_ohlc
from algotrade.indicators import compute_indicators
from algotrade.strategies import golden_cross_signals, ma_crossover_signals, rsi_mean_reversion_signals
from algotrade.validation import walk_forward_evaluate

OUT_DIR = Path("assets")
DATA_PATH = "data/tutorial.csv"
INIT_CASH = 10_000
FEES = 0.001
FREQ = "1D"

COLORS = {
    "close": "#1d3557",
    "sma_fast": "#f4a261",
    "sma_slow": "#9b5de5",
    "sma_long": "#e63946",
    "band": "#adb5bd",
    "Buy & Hold": "#888888",
    "MA Crossover": "#f4a261",
    "RSI Mean Reversion": "#e76f51",
    "Golden Cross": "#2a9d8f",
}

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#333333",
        "axes.labelcolor": "#222222",
        "text.color": "#222222",
        "xtick.color": "#444444",
        "ytick.color": "#444444",
        "axes.grid": True,
        "grid.color": "#e5e5e5",
        "grid.linewidth": 0.8,
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "savefig.dpi": 160,
        "savefig.bbox": "tight",
    }
)


def price_chart(close, high, low):
    ind = compute_indicators(close, high, low, fast_window=20, slow_window=50, long_window=200)

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(close.index, close, color=COLORS["close"], linewidth=1.1, label="Close")
    ax.plot(ind.sma_fast.ma.index, ind.sma_fast.ma, color=COLORS["sma_fast"], linewidth=1.1, label="SMA 20")
    ax.plot(ind.sma_slow.ma.index, ind.sma_slow.ma, color=COLORS["sma_slow"], linewidth=1.1, label="SMA 50")
    ax.plot(ind.sma_long.ma.index, ind.sma_long.ma, color=COLORS["sma_long"], linewidth=1.3, label="SMA 200")
    ax.fill_between(ind.bb.upper.index, ind.bb.lower, ind.bb.upper, color=COLORS["band"], alpha=0.15, label="Bollinger Bands (20, 2σ)")

    ax.set_title("BTC/USD — 5 Years of Daily Price with Moving Averages")
    ax.set_ylabel("Price (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.legend(loc="upper left", frameon=False, ncol=2)
    fig.autofmt_xdate()
    fig.savefig(OUT_DIR / "price_chart.png")
    plt.close(fig)


def equity_curves_chart(close):
    fig, ax = plt.subplots(figsize=(11, 5))

    from algotrade.backtest import run_backtest
    import vectorbt as vbt

    pf_hold = vbt.Portfolio.from_holding(close, init_cash=INIT_CASH, freq=FREQ)
    ax.plot(pf_hold.value().index, pf_hold.value(), color=COLORS["Buy & Hold"], linewidth=1.3, label="Buy & Hold")

    strategies = {
        "MA Crossover": ma_crossover_signals(close, fast=20, slow=50),
        "RSI Mean Reversion": rsi_mean_reversion_signals(close, window=14, lower=30, upper=70),
        "Golden Cross": golden_cross_signals(close, fast=20, long=200),
    }
    for name, (entries, exits) in strategies.items():
        pf = run_backtest(close, entries, exits, init_cash=INIT_CASH, fees=FEES, freq=FREQ)
        ax.plot(pf.value().index, pf.value(), color=COLORS[name], linewidth=1.6, label=name)

    ax.set_yscale("log")
    ax.set_title("Portfolio Value Over Time (log scale, $10,000 start)")
    ax.set_ylabel("Portfolio Value (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.legend(loc="upper left", frameon=False)
    fig.autofmt_xdate()
    fig.savefig(OUT_DIR / "equity_curves.png")
    plt.close(fig)


def comparison_bar_chart(close):
    import vectorbt as vbt

    pf_hold = vbt.Portfolio.from_holding(close, init_cash=INIT_CASH, freq=FREQ)
    strategies = {
        "MA Crossover": ma_crossover_signals(close, fast=20, slow=50),
        "RSI Mean Reversion": rsi_mean_reversion_signals(close, window=14, lower=30, upper=70),
        "Golden Cross": golden_cross_signals(close, fast=20, long=200),
    }
    names = ["Buy & Hold", "MA Crossover", "RSI Mean Reversion", "Golden Cross"]
    returns = [pf_hold.total_return() * 100]
    for name in names[1:]:
        entries, exits = strategies[name]
        pf = run_backtest(close, entries, exits, init_cash=INIT_CASH, fees=FEES, freq=FREQ)
        returns.append(pf.total_return() * 100)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(names, returns, color=[COLORS[n] for n in names], width=0.6)
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_title("In-Sample Total Return by Strategy (5-year backtest)")
    ax.set_ylabel("Total Return [%]")
    ax.grid(axis="x")
    for bar, ret in zip(bars, returns):
        ax.annotate(
            f"{ret:+.0f}%",
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center",
            va="bottom" if ret >= 0 else "top",
            fontsize=10,
            fontweight="bold",
        )
    plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
    fig.savefig(OUT_DIR / "strategy_comparison.png")
    plt.close(fig)


def walk_forward_chart(close):
    param_grid = [
        {"fast": f, "long": l}
        for f in [10, 15, 20, 25, 30]
        for l in [150, 180, 200, 220]
        if f < l
    ]
    result = walk_forward_evaluate(
        close, golden_cross_signals, param_grid,
        n_splits=5, select_metric="total_return",
        init_cash=INIT_CASH, fees=FEES, freq=FREQ,
    )
    frame = result.to_frame()

    fig, ax = plt.subplots(figsize=(9, 5))
    x = range(len(frame))
    width = 0.35
    ax.bar([i - width / 2 for i in x], frame["strategy_return"] * 100, width, color=COLORS["Golden Cross"], label="Golden Cross (out-of-sample)")
    ax.bar([i + width / 2 for i in x], frame["benchmark_return"] * 100, width, color=COLORS["Buy & Hold"], label="Buy & Hold")
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"Fold {i}" for i in x])
    ax.set_ylabel("Return [%]")
    ax.set_title("Walk-Forward Validation: Out-of-Sample Return per Fold")
    ax.legend(loc="upper right", frameon=False)

    win_rate = result.win_rate * 100
    ax.text(
        0.01, 0.02,
        f"Golden Cross beat buy & hold in {win_rate:.0f}% of folds",
        transform=ax.transAxes, fontsize=10, color="#555555", style="italic",
    )
    fig.savefig(OUT_DIR / "walk_forward.png")
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    df = load_ohlc(DATA_PATH)
    close, high, low = df["close"], df["high"], df["low"]

    price_chart(close, high, low)
    equity_curves_chart(close)
    comparison_bar_chart(close)
    walk_forward_chart(close)

    print(f"Saved charts to {OUT_DIR}/")
    for f in sorted(OUT_DIR.glob("*.png")):
        print(f" - {f}")


if __name__ == "__main__":
    main()
