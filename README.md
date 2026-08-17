# AlgoTrade

A BTC/USD backtesting project: an installable Python package (`algotrade`) for indicators, strategies, backtesting, and walk-forward validation, built on [`vectorbt`](https://github.com/polakowo/vectorbt) - plus notebooks and CLI scripts on top of it.

The headline result: a **Golden Cross (SMA 20/200)** strategy beats buy & hold on 5 years of daily BTC/USD data (+179% vs +41%, less than half the drawdown). But walk-forward validation shows that edge mostly evaporates out-of-sample - which is the more important result. See [`notebooks/main.ipynb`](notebooks/main.ipynb) section 7-8 for the full story.

## Project structure

```
AlgoTrade/
├── src/algotrade/        # the package - all reusable logic lives here
│   ├── data.py           #   fetch/load OHLCV data from Bitstamp
│   ├── indicators.py     #   SMA/RSI/MACD/Bollinger/ATR via vectorbt
│   ├── strategies.py     #   signal generators (entries/exits) + a registry
│   ├── backtest.py       #   run a single backtest / compare several
│   └── validation.py     #   expanding-window walk-forward validation
├── notebooks/
│   ├── data.ipynb        # fetches data -> data/tutorial.csv
│   └── main.ipynb        # indicators, 3 strategies, comparison, walk-forward
├── scripts/
│   ├── param_sweep.py    # CLI grid search over MA windows (in-sample)
│   └── walk_forward.py   # CLI walk-forward validation (out-of-sample)
├── tests/                 # pytest unit tests for the package (no network needed)
├── data/tutorial.csv      # 5 years of daily BTC/USD OHLCV (regenerable)
├── results/                # example CSV output from the two scripts
├── pyproject.toml         # `pip install -e .` installs the algotrade package
└── requirements.txt
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

> `vectorbt` requires `numpy<2` (pinned in `pyproject.toml`) - installing a newer numpy in the same environment will break it at import time.

To use the notebooks in Jupyter/VS Code, register the venv as a kernel:

```bash
python -m ipykernel install --user --name=algotrade --display-name="AlgoTrade (.venv)"
```

## Usage

**Notebooks** (in `notebooks/`, run from that directory so relative paths resolve):
- `data.ipynb` - fetches fresh OHLCV data from Bitstamp and saves it to `../data/tutorial.csv`. Adjust `MARKET_SYMBOL`, `STEP`, and `YEARS` in the config cell.
- `main.ipynb` - the main analysis: indicators, three strategies (MA Crossover, RSI Mean Reversion, Golden Cross), a comparison table/chart, and walk-forward validation.

**CLI scripts** (run from the project root):

```bash
python scripts/param_sweep.py          # in-sample grid search over SMA windows
python scripts/walk_forward.py         # out-of-sample walk-forward validation
```

Both accept `--data`, `--fees`, `--freq`, and other flags - run with `--help` to see all options. Both write their full results to `results/`.

**Tests:**

```bash
pytest
```

## Using the package directly

```python
from algotrade.data import load_ohlc
from algotrade.strategies import STRATEGIES, DEFAULT_PARAMS
from algotrade.backtest import compare_strategies

df = load_ohlc("data/tutorial.csv")
close = df["close"]

signals = {name: fn(close, **DEFAULT_PARAMS[name]) for name, fn in STRATEGIES.items()}
print(compare_strategies(close, signals))
```

Adding a new strategy: write a function in `src/algotrade/strategies.py` that takes a close price series and returns `(entries, exits)` boolean Series, then register it in `STRATEGIES` / `DEFAULT_PARAMS`. It automatically becomes available to the comparison table, the notebook, and the sweep/walk-forward scripts.

## Key finding: in-sample vs. out-of-sample

| | In-sample (full history) | Out-of-sample (walk-forward) |
|---|---|---|
| Golden Cross return | +179% | +100% (compounded across folds) |
| Buy & Hold return | +41% | +174% (compounded across folds) |
| Folds/period where strategy wins | - | 1 of 5 |

The parameters (SMA 20/200) were originally chosen by grid-searching the *entire* history, so the in-sample number is optimistic by construction. `scripts/walk_forward.py` / `notebooks/main.ipynb` section 7 re-select parameters on a rolling basis using only past data, which is a much more honest test - and under that test, Golden Cross does not reliably beat buy & hold. Treat the in-sample result as a methodology demonstration, not a trading signal.

## Next steps

- Add stop-loss / take-profit (`sl_stop`, `tp_stop` in `vbt.Portfolio.from_signals`)
- Rolling (not expanding) walk-forward windows, or nested cross-validation
- Combine signals (e.g. only take MA crossover trades when RSI confirms momentum)
- Test on other assets or shorter timeframes to check regime dependence
- Transaction cost / slippage sensitivity analysis

## Disclaimer

For research and educational purposes only - not financial advice. Backtest results, in-sample or out-of-sample, do not predict future performance.
