# AlgoTrade

A small BTC/USD backtesting lab: pull 1-minute OHLCV data from the [Bitstamp API](https://www.bitstamp.net/api/), compute technical indicators, and backtest trading strategies with [`vectorbt`](https://github.com/polakowo/vectorbt).

## Contents

- `main.ipynb` — the backtesting notebook:
  - Loads & prepares OHLCV data
  - Computes indicators: SMA (fast/slow), RSI, MACD, Bollinger Bands, ATR
  - Backtests two strategies — **Moving Average Crossover** (trend-following) and **RSI Mean Reversion** (contrarian)
  - Compares both against a buy & hold benchmark (returns, Sharpe, max drawdown, win rate)
  - Equity curve, drawdown, and trade plots for each strategy
- `data.ipynb` — pulls 1-minute OHLC candles for BTC/USD from Bitstamp's `/api/v2/ohlc/` endpoint.
- `tutorial.csv` — sample OHLCV data (timestamp, open, high, low, close, volume) used by `main.ipynb`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "numpy<2" pandas vectorbt requests ipykernel
```

> `vectorbt` requires `numpy<2` — installing a newer numpy in the same environment will break it at import time.

## Usage

- Run `data.ipynb` to fetch fresh OHLCV data (adjust `market_symbol`, `step`, and `limit` as needed).
- Run `main.ipynb` top to bottom to reproduce the indicators, strategies, and comparison charts. Tune strategy parameters (MA windows, RSI thresholds, fees) in the config cell at the top.

## Disclaimer

For research and educational purposes only — not financial advice. Backtest results on limited historical data do not predict future performance.
